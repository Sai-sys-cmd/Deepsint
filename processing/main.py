from scraper import UniversalScraper, clean_json
from profiler import *
import asyncio
import os
import aiosqlite
import datetime
from summary import summarize_cluster_full

#Use osint.db for testing
DB_PATH = r"HTN-2025\db\osint.db"

def get_versioned_filename(base_path):
    version = 1
    while os.path.exists(base_path + f"_v{version}.json"):
        version += 1
    return base_path + f"_v{version}.json"


async def init_db(db_path=DB_PATH):
    """Create tables if they don't exist."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS user_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            file_path TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            file_path TEXT NOT NULL,
            profile_index INTEGER NOT NULL,
            platform TEXT,
            url TEXT,
            raw_json TEXT, -- store full scraped object as JSON string
            cluster_id TEXT, -- optional: store cluster label
            created_at TEXT NOT NULL,
            UNIQUE(file_path, profile_index)
        )
        """)
        await db.commit()

async def insert_file_to_db_async(username, file_path, db_path=DB_PATH):
    """Insert file record (safe for concurrent async usage)."""
    created_at = datetime.datetime.utcnow().isoformat()
    async with aiosqlite.connect(db_path) as db:
        try:
            await db.execute(
                "INSERT INTO user_files (username, file_path, created_at) VALUES (?, ?, ?)",
                (username, file_path, created_at)
            )
            await db.commit()
        except aiosqlite.IntegrityError:
            # already exists; ignore or update timestamp if you want
            # Optionally: update the created_at or log
            print("UH OH")
            pass

async def insert_profiles_from_json_async(username, file_path, data, clusters=None, db_path=DB_PATH):
    """
    Insert each profile object into `profiles`.
    data should be a list-like object where each element is the scraped profile dict.
    clusters (optional) is a mapping cluster->list_of_indices so we can set cluster_id.
    """
    created_at = datetime.datetime.utcnow().isoformat()
    # build a mapping index -> cluster id (optional)
    index_to_cluster = {}
    if clusters:
        for cluster_id, indices in clusters.items():
            for i in indices:
                index_to_cluster[i] = str(cluster_id)

    async with aiosqlite.connect(db_path) as db:
        insert_sql = """
        INSERT OR IGNORE INTO profiles
          (username, file_path, profile_index, platform, url, raw_json, cluster_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        for idx, profile_obj in enumerate(data):
            platform = profile_obj.get("platform") or profile_obj.get("site") or None
            url = profile_obj.get("url") or profile_obj.get("profile_url") or None
            raw_json = json.dumps(profile_obj, ensure_ascii=False)
            cluster_id = index_to_cluster.get(idx)
            await db.execute(insert_sql, (username, file_path, idx, platform, url, raw_json, cluster_id, created_at))
        await db.commit()        


#Output stuff as a dictionary
async def findProfiles(profileLinks, user):
    """
    This will go through the entire scraping, profiling and summarization process
    profileLinks are the profiles from blackbird, and user will be username/name/email being searched
    user is needed for the file names.
    """    
    
    await init_db()


    #First is scraping
    scraper = UniversalScraper(use_playwright=True, headless=True)
    
    results = await scraper.batch_scrape(profileLinks, 3)
    
    if not results:
        return {}

    #Create file path
    file_path = get_versioned_filename(f"{user}")
    
    scraper.export_results(results, file_path)
    clean_json(file_path)
    #HAVE DATABASE MOVE HERE
    await insert_file_to_db_async(user, file_path)

    #Expect the exported JSON to be a list of profile dicts; adjust if shape differs
    with open(file_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    await insert_profiles_from_json_async(user, file_path, data, clusters=None)

    #Determine Cohere embeddings
    pfp_embeddings, meta_embeddings = calculate_cohere_embeddings(file_path)
    pid_to_label, clusters, combined_sim, dist = cluster_profiles_from_modalities(pfp_embeddings, meta_embeddings)


    profile_info = {}
    for key in clusters.keys():
        profile_info[key] = [[]]
        #Open json scraper file in the database
        #Let's call this data for now
        #Do the json.load() process
        
        for val in clusters[key]:
            profile_info[key][0].append(data[val]["platform"])
        #Add summary here
        
        profile_info[key].append(summarize_cluster_full(clusters[key],file_path, user))
            
    return profile_info

async def main():
    res = await findProfiles(['https://codeforces.com/api/user.info?handles=lordfurno',
            'https://huggingface.co/lordfurno',
            'https://www.wattpad.com/api/v3/users/lordfurno',
            'https://api.imgur.com/account/v1/accounts/lordfurno?client_id=546c25a59c58ad7',
            'https://itch.io/profile/lordfurno',
            'https://hub.docker.com/v2/users/lordfurno/',
            'https://hub.docker.com/v2/orgs/lordfurno/',
            'https://www.kaggle.com/lordfurno',
            'https://www.xboxgamertag.com/search/lordfurno',
            'https://www.last.fm/user/lordfurno',
            'https://api.monkeytype.com/users/lordfurno/profile',
            'https://lichess.org/api/player/autocomplete?term=lordfurno&exists=1',
            'https://api.github.com/users/lordfurno',
            'https://ok.ru/lordfurno'],"LordFurno")
    print(res)
if __name__=="__main__":
    asyncio.run(main())