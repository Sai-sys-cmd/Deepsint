import streamlit as st
import aiosqlite
import json
import asyncio
from datetime import datetime

DB_PATH = "data/osint.db"

async def get_all_results():
    """Retrieve all processing results from database"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                SELECT id, username, total_profiles, clusters_json, file_path, status, created_at
                FROM processing_results 
                ORDER BY created_at DESC
            """)
            rows = await cursor.fetchall()
            
            results = []
            for row in rows:
                result = {
                    "id": row[0],
                    "username": row[1],
                    "total_profiles": row[2],
                    "clusters": json.loads(row[3]) if row[3] else {},
                    "file_path": row[4],
                    "status": row[5],
                    "created_at": row[6]
                }
                results.append(result)
            return results
    except Exception as e:
        st.error(f"Error retrieving results: {e}")
        return []

async def get_result_by_id(result_id):
    """Retrieve specific result by ID"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                SELECT id, username, total_profiles, clusters_json, file_path, status, created_at
                FROM processing_results 
                WHERE id = ?
            """, (result_id,))
            row = await cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "total_profiles": row[2],
                    "clusters": json.loads(row[3]) if row[3] else {},
                    "file_path": row[4],
                    "status": row[5],
                    "created_at": row[6]
                }
            return None
    except Exception as e:
        st.error(f"Error retrieving result: {e}")
        return None

def format_datetime(iso_string):
    """Format ISO datetime string for display"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_string

def show_results_page():
    st.title("📊 OSINT Results")
    
    # Get all results
    results = asyncio.run(get_all_results())
    
    if not results:
        st.info("No results found. Run some searches first!")
        return
    
    # Results overview
    st.subheader("Recent Searches")
    
    # Create columns for the results table
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
    
    with col1:
        st.write("**Username**")
    with col2:
        st.write("**Profiles**")
    with col3:
        st.write("**Clusters**")
    with col4:
        st.write("**Status**")
    with col5:
        st.write("**Date**")
    
    st.divider()
    
    # Display each result
    for result in results:
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
        
        with col1:
            if st.button(f"🔍 {result['username']}", key=f"btn_{result['id']}"):
                st.session_state.selected_result_id = result['id']
        
        with col2:
            st.write(result['total_profiles'])
        
        with col3:
            st.write(len(result['clusters']))
        
        with col4:
            status_color = "🟢" if result['status'] == 'success' else "🔴"
            st.write(f"{status_color} {result['status']}")
        
        with col5:
            st.write(format_datetime(result['created_at']))
    
    # Show detailed view if a result is selected
    if 'selected_result_id' in st.session_state:
        selected_result = asyncio.run(get_result_by_id(st.session_state.selected_result_id))
        
        if selected_result:
            st.divider()
            st.subheader(f"Detailed Results for: {selected_result['username']}")
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Profiles", selected_result['total_profiles'])
            
            with col2:
                st.metric("Clusters Found", len(selected_result['clusters']))
            
            with col3:
                st.metric("Status", selected_result['status'])
            
            with col4:
                st.metric("Date", format_datetime(selected_result['created_at']))
            
            # Display clusters
            if selected_result['clusters']:
                st.subheader("Cluster Analysis")
                
                for cluster_name, cluster_data in selected_result['clusters'].items():
                    with st.expander(f"📁 {cluster_name.replace('_', ' ').title()}", expanded=False):
                        
                        # Cluster summary
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Profile Count:** {cluster_data.get('profile_count', 0)}")
                            st.write(f"**Platforms:** {', '.join(cluster_data.get('platforms', []))}")
                        
                        with col2:
                            if 'summary' in cluster_data:
                                st.write("**Summary:**")
                                st.write(cluster_data['summary'])
                        
                        # Show profiles in this cluster
                        if 'profiles' in cluster_data and cluster_data['profiles']:
                            st.write("**Profiles:**")
                            for i, profile in enumerate(cluster_data['profiles'], 1):
                                platform = profile.get('platform', 'Unknown')
                                url = profile.get('url', 'No URL')
                                st.write(f"{i}. **{platform}**: {url}")
            
            # Clear selection button
            if st.button("← Back to Results List"):
                del st.session_state.selected_result_id
                st.rerun()
    
    # Refresh button
    if st.button("🔄 Refresh Results"):
        st.rerun()
