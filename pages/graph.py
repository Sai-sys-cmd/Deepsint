import streamlit as st
import json
import os
import math
import warnings
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as patches
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
# === Performance & rate-limit protections ===
from functools import wraps
import time
import random
import threading

# Limits
MAX_NODES = 400        # maximum profiles to layout/plot (sample if more)
MAX_EDGES_PER_NODE = 30  # only keep top-k strongest edges per node
LAYOUT_ITER_BASE = 50   # base iterations for layout; will scale by graph size
EMBED_TIMEOUT = 25      # seconds to wait for external embedding call
EMBED_RETRIES = 2       # retry count for embedding calls
DB_PATH = "data/osint.db"

# simple retry-with-timeout wrapper for blocking calls (profiler)
def call_with_timeout_and_retries(fn, timeout=EMBED_TIMEOUT, retries=EMBED_RETRIES, *args, **kwargs):
    last_exc = None
    for attempt in range(retries+1):
        result = [None]
        exc = [None]
        def target():
            try:
                result[0] = fn(*args, **kwargs)
            except Exception as e:
                exc[0] = e
        t = threading.Thread(target=target, daemon=True)
        t.start()
        t.join(timeout)
        if t.is_alive():
            # timed out
            last_exc = TimeoutError(f"call timed out after {timeout}s")
            # continue to retry
        else:
            if exc[0] is not None:
                last_exc = exc[0]
                # retry unless last attempt
            else:
                return result[0]
    # exhausted retries
    raise last_exc or RuntimeError("unknown error in call_with_timeout_and_retries")

# Cache embedding / similarity building to avoid repeated expensive runs
@st.cache_data(show_spinner=False)
def cached_build_similarity(pfp_embeddings, meta_embeddings):
    return build_similarity_matrix_from_embeddings(pfp_embeddings, meta_embeddings)

@st.cache_data(show_spinner=False)
def cached_profiler_embeddings(file_path):
    # wrap profiler call with timeout & retries to avoid hung external calls
    try:
        from processing import profiler
    except Exception as e:
        raise e
    # call profiler.calculate_cohere_embeddings with timeout/retries
    return call_with_timeout_and_retries(profiler.calculate_cohere_embeddings, EMBED_TIMEOUT, EMBED_RETRIES, file_path)


# Page config
st.set_page_config(
    page_title="🔍 Deepsint Profile Visualizer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stAlert > div {
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions from your original code
def ensure_array_like_embeddings(embed_source):
    mapping = {}
    if embed_source is None:
        return mapping
    if isinstance(embed_source, dict):
        for k, v in embed_source.items():
            mapping[int(k)] = np.array(v)
    else:
        for i, v in enumerate(embed_source):
            if v is None:
                continue
            mapping[int(i)] = np.array(v)
    return mapping

def build_similarity_matrix_from_embeddings(pfp_embeddings, meta_embeddings):
    pfp_map = ensure_array_like_embeddings(pfp_embeddings)
    meta_map = ensure_array_like_embeddings(meta_embeddings)
    all_pids = sorted(set(list(pfp_map.keys()) + list(meta_map.keys())))
    emb_list = []
    for pid in all_pids:
        if pid in meta_map:
            emb_list.append(meta_map[pid])
        elif pid in pfp_map:
            emb_list.append(pfp_map[pid])
        else:
            emb_list.append(np.zeros(64))
    if len(emb_list) == 0:
        return None, [], {}
    E = np.vstack([np.asarray(e).ravel() for e in emb_list])
    if np.allclose(E, 0):
        E = E + 1e-6 * np.random.RandomState(0).randn(*E.shape)
    sim = cosine_similarity(E)
    return sim, all_pids, {pid: idx for idx, pid in enumerate(all_pids)}

def create_interactive_network_graph(file_path, similarity_matrix=None, clusters=None, 
                                   pid_to_label=None, similarity_threshold=0.5):
    """Create an interactive Plotly network graph"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        profiles_data = json.load(f)

    G = nx.Graph()
    node_info = {}
    
    for i, profile in enumerate(profiles_data):
        status = profile.get("scrape_status", "ok")
        if status == "failed":
            continue
        platform = profile.get("platform", "unknown")
        cluster_id = None
        if pid_to_label and isinstance(pid_to_label, dict):
            cluster_id = pid_to_label.get(i, -1)
        username = profile.get("username") or profile.get("user") or f"P{i}"
        bio = (profile.get("bio") or "")[:200]
        
        G.add_node(i, platform=platform, cluster=cluster_id, username=username, bio=bio)
        node_info[i] = {
            'username': username,
            'platform': platform,
            'cluster': cluster_id,
            'bio': bio,
            'display_name': profile.get("display_name", ""),
            'followers': profile.get("followers"),
            'url': profile.get("url", "")
        }

    # Add edges based on similarity
    if similarity_matrix is not None and len(G.nodes):
        sim = np.array(similarity_matrix)
        nodes = sorted(G.nodes())
        for idx_i, pid_i in enumerate(nodes):
            for idx_j, pid_j in enumerate(nodes[idx_i+1:], idx_i+1):
                val = None
                if sim.shape[0] > max(pid_i, pid_j):
                    val = float(sim[pid_i, pid_j])
                elif sim.shape[0] == len(nodes):
                    val = float(sim[idx_i, idx_j])
                if val is None or math.isnan(val) or val <= similarity_threshold:
                    continue
                G.add_edge(pid_i, pid_j, weight=float(val))

    if len(G) == 0:
        return None, None

    # Create layout
    pos = nx.spring_layout(G, k=0.8, iterations=200, seed=42, weight='weight')
    
    # Prepare node data
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []
    hover_text = []
    
    platforms = list(set(G.nodes[n]['platform'] for n in G.nodes()))
    color_palette = px.colors.qualitative.Set3
    platform_colors = {p: color_palette[i % len(color_palette)] for i, p in enumerate(platforms)}
    
    deg = dict(nx.degree(G))
    max_degree = max(deg.values()) if deg else 1
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        info = node_info[node]
        username = info['username']
        platform = info['platform']
        cluster = info['cluster']
        
        # print(cluster)
        # Node size based on degree
        size = 20 + (deg.get(node, 0) / max(0.01,max_degree)) * 30
        node_sizes.append(size)
        
        # Node color based on platform
        node_colors.append(platform_colors.get(platform, '#gray'))
        
        # Hover text with detailed info
        hover_info = f"<b>{username}</b><br>"
        hover_info += f"Platform: {platform}<br>"
        if cluster is not None and cluster != -1:
            hover_info += f"Cluster: {cluster}<br>"
        if info['display_name']:
            hover_info += f"Name: {info['display_name']}<br>"
        if info['followers']:
            hover_info += f"Followers: {info['followers']:,}<br>"
        if info['bio']:
            hover_info += f"Bio: {info['bio'][:100]}...<br>"
        if info['url']:
            hover_info += f"URL: {info['url']}"
        
        hover_text.append(hover_info)
        node_text.append(username[:10])
    
    # Prepare edge data
    edge_x = []
    edge_y = []
    edge_weights = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_weights.append(edge[2].get('weight', 0))

    # Create the plot
    fig = go.Figure()

    # Add edges
    if edge_weights:
        max_weight = max(edge_weights) if edge_weights else 1
        # Create edge traces with varying opacity based on weight
        for i in range(0, len(edge_x), 3):
            if i//3 < len(edge_weights):
                weight = edge_weights[i//3]
                opacity = 0.3 + 0.7 * (weight / max_weight)
                width = 0.5 + 3 * (weight / max_weight)
                fig.add_trace(go.Scatter(
                    x=edge_x[i:i+2], y=edge_y[i:i+2],
                    mode='lines',
                    line=dict(width=width, color='rgba(100,100,100,0.5)'),
                    showlegend=False,
                    hoverinfo='none'
                ))

    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='black'),
            opacity=0.8
        ),
        text=node_text,
        textposition="middle center",
        textfont=dict(size=8, color='white'),
        hovertext=hover_text,
        hoverinfo='text',
        showlegend=False
    ))

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"Interactive OSINT Profile Network<br>({len(G.nodes())} profiles, {len(G.edges())} connections)",
            x=0.5,
            font=dict(size=16)
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        annotations=[ 
            dict(
                text="Drag to pan, scroll to zoom. Node size = connections. Hover for details.",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='gray', size=12)
            )
        ],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(240,240,240,0.1)'
    )
    
    return fig, G

def create_cluster_overview(clusters, profiles_data):
    """Create cluster overview visualization"""
    if not clusters:
        return None
    
    cluster_stats = []
    for cluster_id, profile_ids in clusters.items():
        platforms = []
        usernames = []
        for pid in profile_ids:
            if pid < len(profiles_data):
                profile = profiles_data[pid]
                platforms.append(profile.get('platform', 'unknown'))
                usernames.append(profile.get('username', f'P{pid}'))
        
        cluster_stats.append({
            'Cluster': f"Cluster {cluster_id}",
            'Size': len(profile_ids),
            'Platforms': len(set(platforms)),
            'Platform List': ', '.join(set(platforms)),
            'Profiles': ', '.join(usernames[:5]) + ('...' if len(usernames) > 5 else '')
        })
    
    df = pd.DataFrame(cluster_stats)
    return df

def create_platform_distribution(profiles_data):
    """Create platform distribution chart"""
    platforms = []
    for profile in profiles_data:
        if profile.get("scrape_status") != "failed":
            platforms.append(profile.get('platform', 'unknown'))
    
    platform_counts = pd.Series(platforms).value_counts()
    
    fig = px.pie(
        values=platform_counts.values,
        names=platform_counts.index,
        title="Profile Distribution by Platform"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def main():
    st.markdown('<h1 class="main-header">🔍 Deepsint Profile Visualizer</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("## 📁 Data Upload")
    
    # File upload option
    uploaded_file = st.sidebar.file_uploader(
        "Upload JSON file", 
        type=['json'],
        help="Upload your scraped profiles JSON file"
    )
    
    # Or file path input
    directory_path = r"data\scraping"

    # List the files in the directory
    files = [f for f in os.listdir(directory_path) if f.endswith('.json')]  # Filter to only JSON files

    #Add a dropdown with the file names
    file_path_input = st.sidebar.selectbox(
        "Select a file from the directory:",
        files,
        help="Select a JSON file from the specified directory"
    )

    # Construct the full file path
    full_file_path = os.path.join(directory_path, file_path_input)

    
    # Settings
    st.sidebar.markdown("## ⚙️ Visualization Settings")
    similarity_threshold = st.sidebar.slider(
        "Similarity Threshold", 
        min_value=0.1, 
        max_value=1.0, 
        value=0.5, 
        step=0.1,
        help="Minimum similarity to show connections"
    )
    
    show_isolated = st.sidebar.checkbox(
        "Show isolated nodes", 
        value=True,
        help="Show profiles with no connections"
    )
    
    # Determine file path
    file_path = None
    profiles_data = None
    
    if uploaded_file is not None:
        try:
            profiles_data = json.load(uploaded_file)
            file_path = uploaded_file
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
            return
    elif full_file_path and os.path.exists(full_file_path):
        file_path = full_file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                profiles_data = json.load(f)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return
    
    if profiles_data is None:
        st.info("👆 Please upload a JSON file or enter a valid file path in the sidebar")
        st.markdown("""
        ### Expected JSON format:
        ```json
        [
            {
                "username": "user1",
                "platform": "github.com",
                "scrape_status": "ok",
                "bio": "Software developer",
                "followers": 100
            }
        ]
        ```
        """)
        return
    
    # Load and process data
    with st.spinner("🔄 Processing profiles and calculating similarities..."):
        try:
            # Try to import your profiler
            from processing import profiler
            pfp_embeddings, meta_embeddings = profiler.calculate_cohere_embeddings(file_path)
            pid_to_label, clusters, combined_sim, dist = profiler.cluster_profiles_from_modalities(
                pfp_embeddings, meta_embeddings)

            # print(clusters)
            
            st.success("✅ Successfully loaded embeddings and clustering data!")
            
        except Exception as e:
            st.warning(f"⚠️ Could not load profiler module: {e}")
            st.info("📊 Creating basic visualization without ML embeddings...")
            
            # Fallback: create basic similarity based on text features
            pfp_embeddings, meta_embeddings = {}, {}
            combined_sim, profile_ids, pid_index = build_similarity_matrix_from_embeddings({}, {})
            clusters = {}
            pid_to_label = {}
    
    # Overview metrics
    st.markdown("## 📊 Overview")
    
    total_profiles = len([p for p in profiles_data if p.get('scrape_status') != 'failed'])
    total_platforms = len(set(p.get('platform', 'unknown') for p in profiles_data 
                            if p.get('scrape_status') != 'failed'))
    total_clusters = len(clusters) if clusters else 0
    # print(clusters)
    
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Total Profiles", total_profiles)
    with col2:
        st.metric("🌐 Platforms", total_platforms)
    with col3:
        st.metric("🎯 Identity Clusters", total_clusters)
    with col4:
        avg_cluster_size = sum(len(v) for v in clusters.values()) / len(clusters) if clusters else 0
        st.metric("👥 Avg Cluster Size", f"{avg_cluster_size:.1f}")
    
    # Main visualization
    st.markdown("## 🕸️ Interactive Network Graph")
    
    if uploaded_file:
        # For uploaded files, we need to save temporarily to use with your functions
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(profiles_data, f)
            temp_file_path = f.name
        file_path = temp_file_path
    
    fig, graph = create_interactive_network_graph(
        file_path, combined_sim, clusters, pid_to_label, similarity_threshold
    )
    
    if fig:
        st.plotly_chart(fig, width='stretch')
        
        # Graph statistics
        st.markdown("### 📈 Network Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nodes", len(graph.nodes()))
        with col2:
            st.metric("Edges", len(graph.edges()))
        with col3:
            density = nx.density(graph)
            st.metric("Density", f"{density:.3f}")
    else:
        st.error("Could not create network visualization")
    
    # Additional visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥧 Platform Distribution")
        platform_fig = create_platform_distribution(profiles_data)
        st.plotly_chart(platform_fig, width='stretch')
    
    with col2:
        st.markdown("### 🎯 Identity Clusters")
        if clusters:
            cluster_df = create_cluster_overview(clusters, profiles_data)
            st.dataframe(cluster_df, width='stretch')
        else:
            st.info("No clusters found")
    
    # Profile details table
    st.markdown("## 📋 Profile Details")
    
    # Create profiles dataframe
        # Create profiles dataframe
    profile_df = []
    for i, profile in enumerate(profiles_data):
        if profile.get('scrape_status') != 'failed':
            cluster_id = pid_to_label.get(i, -1) if pid_to_label else -1
            # Use pd.NA for missing cluster so dtype can be nullable integer
            cluster_val = cluster_id if cluster_id != -1 else pd.NA
            followers_val = profile.get('followers', pd.NA)
            bio_short = (profile.get('bio', '') or '')[:100]
            profile_df.append({
                'ID': i,
                'Username': profile.get('username', f'P{i}'),
                'Platform': profile.get('platform', 'unknown'),
                'Cluster': cluster_val,
                'Followers': followers_val,
                'Bio': bio_short + ('...' if len(profile.get('bio', '') or '') > 100 else ''),
                'Status': profile.get('scrape_status', 'ok')
            })

    if profile_df:
        df = pd.DataFrame(profile_df)
        # Convert Cluster to pandas nullable integer dtype (allows pd.NA)
        try:
            df['Cluster'] = df['Cluster'].astype('Int64')
        except Exception:
            # fallback: keep as string if conversion fails for any reason
            df['Cluster'] = df['Cluster'].astype(str)

        # Also make Followers numeric if possible, otherwise nullable Int
        try:
            df['Followers'] = pd.to_numeric(df['Followers'], errors='coerce').astype('Int64')
        except Exception:
            # keep original
            pass

        st.dataframe(df, width='stretch')

    
    # Download processed data
    if st.button("📥 Download Analysis Results"):
        results = {
            'profiles': profiles_data,
            'clusters': clusters,
            'pid_to_label': pid_to_label,
            'similarity_threshold': similarity_threshold,
            'total_profiles': total_profiles,
            'total_platforms': total_platforms
        }
        
        st.download_button(
            label="Download JSON",
            data=json.dumps(results, indent=2),
            file_name="Deepsint_analysis_results.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()