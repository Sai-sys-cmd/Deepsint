from database import get_db_connection

def save_profile_to_db(profile):
    """
    Save a Profile object to the database.
    Each profile can have multiple links stored as separate rows.
    """
    conn = get_db_connection()
    
    # Save main URL
    conn.execute(
        "INSERT INTO results (query, source, data) VALUES (?, ?, ?)",
        (profile.username, profile.platform, profile.url)
    )
    
    # Save social links
    for link in getattr(profile, 'social_links', []):
        conn.execute(
            "INSERT INTO results (query, source, data) VALUES (?, ?, ?)",
            (profile.username, 'SocialLink', link)
        )
    
    # Save other links
    for link in getattr(profile, 'links', []):
        conn.execute(
            "INSERT INTO results (query, source, data) VALUES (?, ?, ?)",
            (profile.username, 'WebLink', link)
        )
    
    conn.commit()
    conn.close()
