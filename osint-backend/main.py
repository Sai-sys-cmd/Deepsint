from fastapi import FastAPI
from database import get_db_connection, init_db
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, parse_qs

app = FastAPI(title="OSINT Visualizer Backend")
init_db()

# ------------------------
# Test route
# ------------------------
@app.get("/")
def read_root():
    return {"message": "Hello Hack the North!"}

# ------------------------
# GitHub scraping
# ------------------------
def fetch_github(username):
    url = f"https://api.github.com/users/{username}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return {"platform": "GitHub", "url": data.get("html_url")}
    return None

# ------------------------
# Reddit scraping
# ------------------------
def fetch_reddit(username):
    url = f"https://www.reddit.com/user/{username}/about.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()["data"]
        return {"platform": "Reddit", "url": f"https://reddit.com/user/{username}"}
    return None

# ------------------------
# DuckDuckGo web search scraping
# ------------------------
def fetch_web_search(username):
    url = f"https://duckduckgo.com/html/?q={username}"
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    results = []
    for a in soup.find_all("a", class_="result__a", href=True):
        # Decode DuckDuckGo link
        parsed = urlparse(a['href'])
        qs = parse_qs(parsed.query)
        if 'uddg' in qs:
            real_url = unquote(qs['uddg'][0])
            # Detect platform from URL
            domain = urlparse(real_url).netloc.lower()
            if "github.com" in domain:
                platform = "GitHub"
            elif "linkedin.com" in domain:
                platform = "LinkedIn"
            elif "instagram.com" in domain:
                platform = "Instagram"
            elif "reddit.com" in domain:
                platform = "Reddit"
            else:
                platform = "Web"
            results.append({"platform": platform, "url": real_url})
    return results[:5]  # top 5 links

# ------------------------
# OSINT search endpoint
# ------------------------
def perform_search(username: str):
    results = []

    github = fetch_github(username)
    if github:
        results.append(github)

    reddit = fetch_reddit(username)
    if reddit:
        results.append(reddit)

    web_results = fetch_web_search(username)
    results.extend(web_results)

    # Save results in DB
    if results:
        conn = get_db_connection()
        for r in results:
            # Avoid duplicates
            conn.execute(
                "INSERT OR IGNORE INTO results (query, source, data) VALUES (?, ?, ?)",
                (username, r["platform"], r["url"])
            )
        conn.commit()
        conn.close()
    return results

@app.get("/search/{username}")
def search_username(username: str):
    results = perform_search(username)
    return {"query": username, "results": results}

# ------------------------
# Get past results or scrape if empty
# ------------------------
@app.get("/results/{username}")
def get_results(username: str):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT source, data FROM results WHERE query = ?", (username,)
    ).fetchall()

    if not rows:
        # Auto-scrape if no results yet
        results = perform_search(username)
        rows = [{"source": r["platform"], "data": r["url"]} for r in results]
    else:
        rows = [{"source": row["source"], "data": row["data"]} for row in rows]

    conn.close()
    return {"query": username, "results": rows}
