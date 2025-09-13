from scraper import UniversalScraper, clean_json
from profiler import *
import asyncio
import os
import sqlite3
from summary import summarize_cluster_full

def get_versioned_filename(base_path):
    version = 1
    while os.path.exists(base_path + f"_v{version}.json"):
        version += 1
    return base_path + f"_v{version}.json"

def insert_file_to_db(user, file_path):
    conn = sqlite3.connect("osint.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO user_profiles (user, file_path)
            VALUES (?, ?)
        ''', (user, file_path))
        
        #Commit the transaction
        conn.commit()
        
    except sqlite3.IntegrityError:
        #File path already exsists
        print(f"Record for {user} with file path {file_path} already exists.")
    
    finally:
        #Close the connection
        conn.close()

        


#Output stuff as a dictionary
async def findProfiles(profileLinks, user):
    """
    This will go through the entire scraping, profiling and summarization process
    profileLinks are the profiles from blackbird, and user will be username/name/email being searched
    user is needed for the file names.
    """    
    #First is scraping
    scraper = UniversalScraper(use_playwright=True, headless=True)
    
    results = await scraper.batch_scrape(profileLinks, 3)
    
    if results:
        #Create file path
        file_path = get_versioned_filename(f"{user}")
        
        scraper.export_results(results, file_path)
        clean_json(file_path)
        #HAVE DATABASE MOVE HERE
        
        #Determine Cohere embeddings for data
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
            
            profile_info[key].append(summarize_cluster_full(clusters[key],DBJSONPATH, user))
                
        return profile_info
    else:
        raise ValueError(f"No results found for user: {user}")


