import streamlit as st
import aiosqlite
import json
import asyncio
from datetime import datetime
import pandas as pd
DB_PATH = "data/osint.db"
async def get_search_history():
    """Retrieve search history from database"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                SELECT uf.username, uf.file_path, uf.created_at,
                       COUNT(p.id) as profile_count,
                       COUNT(DISTINCT p.cluster_id) as cluster_count,
                       GROUP_CONCAT(DISTINCT p.platform) as platforms
                FROM user_files uf
                LEFT JOIN profiles p ON uf.file_path = p.file_path
                GROUP BY uf.username, uf.file_path, uf.created_at
                ORDER BY uf.created_at DESC
            """)
            rows = await cursor.fetchall()
            history = []
            for row in rows:
                history.append({
                    "username": row[0],
                    "file_path": row[1],
                    "created_at": row[2],
                    "profile_count": row[3] or 0,
                    "cluster_count": row[4] or 0,
                    "platforms": row[5].split(',') if row[5] else []
                })
            return history
    except Exception as e:
        st.error(f"Error retrieving search history: {e}")
        return []
async def get_profile_details(file_path):
    """Get detailed profile information for a specific search"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                SELECT platform, url, cluster_id, raw_json
                FROM profiles
                WHERE file_path = ?
                ORDER BY cluster_id, platform
            """, (file_path,))
            rows = await cursor.fetchall()
            profiles = []
            for row in rows:
                profile_data = {
                    "platform": row[0],
                    "url": row[1],
                    "cluster_id": row[2],
                    "raw_data": json.loads(row[3]) if row[3] else {}
                }
                profiles.append(profile_data)
            return profiles
    except Exception as e:
        st.error(f"Error retrieving profile details: {e}")
        return []
async def delete_search_record(file_path):
    """Delete a search record and all associated profiles"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Delete profiles first (foreign key constraint)
            await db.execute("DELETE FROM profiles WHERE file_path = ?", (file_path,))
            # Delete user file record
            await db.execute("DELETE FROM user_files WHERE file_path = ?", (file_path,))
            await db.commit()
            return True
    except Exception as e:
        st.error(f"Error deleting search record: {e}")
        return False
def format_datetime(iso_string):
    """Format ISO datetime string for display"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_string
def show_history_page():
    st.title(":books: Search History")
    st.markdown("View and manage your OSINT search history and results.")
    # Get search history
    history = asyncio.run(get_search_history())
    if not history:
        st.info("No search history found. Start by running some searches!")
        return
    # Search and filter options
    col1, col2 = st.columns([2, 1])
    with col1:
        search_filter = st.text_input(":mag: Filter by username:", placeholder="Enter username to filter...")
    with col2:
        sort_option = st.selectbox("Sort by:", ["Date (Newest)", "Date (Oldest)", "Username", "Profile Count"])
    # Apply filters
    filtered_history = history
    if search_filter:
        filtered_history = [h for h in history if search_filter.lower() in h["username"].lower()]
    # Apply sorting
    if sort_option == "Date (Oldest)":
        filtered_history = sorted(filtered_history, key=lambda x: x["created_at"])
    elif sort_option == "Username":
        filtered_history = sorted(filtered_history, key=lambda x: x["username"].lower())
    elif sort_option == "Profile Count":
        filtered_history = sorted(filtered_history, key=lambda x: x["profile_count"], reverse=True)
    # Default is already "Date (Newest)"
    st.divider()
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Searches", len(history))
    with col2:
        total_profiles = sum(h["profile_count"] for h in history)
        st.metric("Total Profiles", total_profiles)
    with col3:
        unique_users = len(set(h["username"] for h in history))
        st.metric("Unique Users", unique_users)
    with col4:
        avg_profiles = total_profiles / len(history) if history else 0
        st.metric("Avg Profiles/Search", f"{avg_profiles:.1f}")
    st.divider()
    # Display history entries
    st.subheader(f"Search History ({len(filtered_history)} entries)")
    for i, entry in enumerate(filtered_history):
        with st.expander(
            f":mag: {entry['username']} - {format_datetime(entry['created_at'])} "
            f"({entry['profile_count']} profiles, {entry['cluster_count']} clusters)",
            expanded=False
        ):
            # Entry details
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Username:** {entry['username']}")
                st.write(f"**Date:** {format_datetime(entry['created_at'])}")
                st.write(f"**File Path:** {entry['file_path']}")
                if entry['platforms']:
                    st.write("**Platforms Found:**")
                    platforms_text = ", ".join([p.strip() for p in entry['platforms'] if p.strip()])
                    st.write(platforms_text)
            with col2:
                st.metric("Profiles", entry['profile_count'])
                st.metric("Clusters", entry['cluster_count'])
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f":clipboard: View Details", key=f"details_{i}"):
                    st.session_state[f"show_details_{entry['file_path']}"] = True
            with col2:
                if st.button(f":bar_chart: View in Results", key=f"results_{i}"):
                    st.session_state.selected_result_username = entry['username']
                    st.switch_page("pages/results.py")
            with col3:
                if st.button(f":wastebasket: Delete", key=f"delete_{i}", type="secondary"):
                    if st.session_state.get(f"confirm_delete_{entry['file_path']}", False):
                        # Actually delete
                        success = asyncio.run(delete_search_record(entry['file_path']))
                        if success:
                            st.success("Search record deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete search record.")
                    else:
                        # Show confirmation
                        st.session_state[f"confirm_delete_{entry['file_path']}"] = True
                        st.warning("Click delete again to confirm deletion.")
            # Show detailed profile information if requested
            if st.session_state.get(f"show_details_{entry['file_path']}", False):
                st.divider()
                st.write("**Detailed Profile Information:**")
                profiles = asyncio.run(get_profile_details(entry['file_path']))
                if profiles:
                    # Group by cluster
                    clusters = {}
                    for profile in profiles:
                        cluster_id = profile['cluster_id'] or 'unclustered'
                        if cluster_id not in clusters:
                            clusters[cluster_id] = []
                        clusters[cluster_id].append(profile)
                    for cluster_id, cluster_profiles in clusters.items():
                        st.write(f"**Cluster {cluster_id}:**")
                        for profile in cluster_profiles:
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.write(f"• {profile['platform']}")
                            with col2:
                                if profile['url']:
                                    st.write(f"[{profile['url']}]({profile['url']})")
                                else:
                                    st.write("No URL")
                        st.write("")
                if st.button(f"Hide Details", key=f"hide_{i}"):
                    st.session_state[f"show_details_{entry['file_path']}"] = False
                    st.rerun()
    # Bulk operations
    if filtered_history:
        st.divider()
        st.subheader("Bulk Operations")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(":wastebasket: Clear All History", type="secondary"):
                if st.session_state.get("confirm_clear_all", False):
                    # Delete all records
                    try:
                        async def clear_all():
                            async with aiosqlite.connect(DB_PATH) as db:
                                await db.execute("DELETE FROM profiles")
                                await db.execute("DELETE FROM user_files")
                                await db.commit()
                        asyncio.run(clear_all())
                        st.success("All search history cleared!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing history: {e}")
                else:
                    st.session_state["confirm_clear_all"] = True
                    st.warning("Click again to confirm clearing ALL search history.")
        with col2:
            if st.button(":inbox_tray: Export History"):
                # Create DataFrame for export
                export_data = []
                for entry in history:
                    export_data.append({
                        "Username": entry["username"],
                        "Date": entry["created_at"],
                        "Profiles": entry["profile_count"],
                        "Clusters": entry["cluster_count"],
                        "Platforms": ", ".join(entry["platforms"])
                    })
                df = pd.DataFrame(export_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label=":inbox_tray: Download CSV",
                    data=csv,
                    file_name=f"osint_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    # Refresh button
    if st.button(":arrows_counterclockwise: Refresh History"):
        st.rerun()
if __name__ == "__main__":
    show_history_page()