# pages/results.py
import streamlit as st
import json
import os
import glob
import math
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Deepsint Results", layout="wide")

# Helper functions ----------------------------------------------------------
def find_latest_result_file():
    files = glob.glob("data/results_*.json")
    if not files:
        return None
    # pick latest by modified time
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def load_json_file(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

def get_profile_cards(cluster_sites, cluster_summary, raw_profiles=None):
    """
    Build a list of profile-card dicts to render. If raw_profiles provided (list of dicts),
    try to match indices or urls to give richer cards (avatar, bio).
    If not, we'll just create simple cards from site strings.
    """
    cards = []
    # If cluster_sites contains indices, or full dicts, handle them:
    for entry in cluster_sites:
        card = {"title": None, "url": None, "platform": None, "bio": None, "avatar": None}
        if isinstance(entry, dict):
            # full profile dict
            card["title"] = entry.get("username") or entry.get("name") or entry.get("platform")
            card["url"] = entry.get("url")
            card["platform"] = entry.get("platform") or entry.get("site")
            card["bio"] = entry.get("bio") or entry.get("description") or entry.get("summary")
            card["avatar"] = entry.get("avatar") or entry.get("image")
        elif isinstance(entry, int) and raw_profiles and 0 <= entry < len(raw_profiles):
            r = raw_profiles[entry]
            card["title"] = r.get("username") or r.get("name") or r.get("platform")
            card["url"] = r.get("url")
            card["platform"] = r.get("platform") or r.get("site")
            card["bio"] = r.get("bio") or r.get("description")
            card["avatar"] = r.get("avatar")
        else:
            # assume it's just a site string (or url)
            s = str(entry)
            card["title"] = s
            # if it looks like a URL, set url
            if s.startswith("http://") or s.startswith("https://"):
                card["url"] = s
            else:
                # keep as platform label
                card["platform"] = s
        cards.append(card)
    return cards

# CSS for rounded card look -------------------------------------------------
st.markdown(
    """
    <style>
    .card {
        border-radius: 12px;
        padding: 14px;
        background: #ffffff;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        margin-bottom: 12px;
        border: 1px solid rgba(0,0,0,0.04);
    }
    .card-title { font-weight: 600; font-size: 16px; margin-bottom: 6px; }
    .card-platform { font-size: 13px; color: #666; margin-bottom: 8px; }
    .badge { display:inline-block; padding:6px 10px; border-radius:999px; background:#f1f5f9; margin-right:6px; font-size:12px; }
    .summary { margin-top:8px; color:#111; }
    .url { font-size:13px; color:#0b5fff; text-decoration: none; }
    .card-grid { display:flex; flex-wrap: wrap; gap: 12px; }
    .card-col { flex: 1 1 320px; max-width: 420px; min-width: 260px; }
    </style>
    """, unsafe_allow_html=True
)

# Page: determine which result file to load --------------------------------
qp = st.experimental_get_query_params()
file_param = qp.get("file", [None])[0]

if file_param:
    result_file = os.path.join("data", file_param) if not os.path.isabs(file_param) else file_param
    if not os.path.exists(result_file):
        st.warning(f"Requested results file not found: {result_file}. Loading latest instead.")
        result_file = find_latest_result_file()
else:
    result_file = find_latest_result_file()

if not result_file:
    st.title("Deepsint Results")
    st.info("No results file found. Run a search from the Home page first.")
    st.stop()

# load results and raw profiles if available
try:
    info = load_json_file(result_file)
except Exception as e:
    st.error(f"Failed to load results file: {e}")
    st.stop()

# try to load raw profiles (optional)
basename = os.path.basename(result_file)
# assume raw file is raw_{username}.json or raw_latest.json
username = basename.replace("results_", "").replace(".json", "")


# Header
st.header("Deepsint Results")
st.markdown(f"*Loaded:* `{result_file}` — **{len(info)}** cluster(s) found.")
st.markdown("---")

# For each cluster: render a block with cluster header + rounded cards
for cluster_key in sorted(info.keys(), key=lambda x: int(x) if str(x).isdigit() else x):
    cluster_val = info[cluster_key]
    # defensive unpack: we expect [sites_list, summary_text, optional_indices...]
    sites = []
    summary_text = ""
    extra = None
    if isinstance(cluster_val, list):
        if len(cluster_val) >= 1:
            sites = cluster_val[0] if isinstance(cluster_val[0], (list,tuple)) else [cluster_val[0]]
        if len(cluster_val) >= 2:
            summary_text = cluster_val[1] or ""
        if len(cluster_val) >= 3:
            extra = cluster_val[2]

    # If extra is present and is list of indices, merge into sites for richer cards
    if extra and isinstance(extra, list):
        # allow extra to override sites entries, e.g. indices into raw_profiles
        sites = extra

    st.subheader(f"Cluster {cluster_key} — {len(sites)} item(s)")
    if summary_text:
        st.write(summary_text)

    # Build profile card objects
    cards = get_profile_cards(sites, summary_text)

    # Render grid of cards (3 columns responsive)
    cols_per_row = 3
    # We'll use a manual columns loop that fills row by row
    card_cols = st.columns(cols_per_row)
    col_idx = 0
    import textwrap
    
for card in cards:
    c = card_cols[col_idx]
    with c:
        title = card.get("title") or "Profile"
        platform = card.get("platform") or ""
        url = card.get("url")
        bio = card.get("bio") or ""
        avatar = card.get("avatar")

        avatar_html = ""
        if avatar:
            avatar_html = (
                f'<img src="{avatar}" '
                'style="width:48px;height:48px;border-radius:50%;object-fit:cover;'
                'margin-right:10px;vertical-align:middle;" />'
            )

        # Build HTML (no leading newline)
        card_html = f'''
        <div class="card">
        <div style="display:flex; align-items:center;">
            {avatar_html}
            <div style="flex:1;">
            <div class="card-title">{title}</div>
            <div class="card-platform">{platform}</div>
            </div>
        </div>
        <div style="margin-top:8px;">
        '''
        if bio:
            short_bio = bio if len(bio) < 300 else bio[:300] + "…"
            card_html += f'<div class="summary">{short_bio}</div>'
        if url:
            card_html += f'<div style="margin-top:8px;"><a class="url" href="{url}" target="_blank">{url}</a></div>'

        card_html += "</div></div>"

        # remove indentation/newline that causes Markdown to treat it as code
        card_html = textwrap.dedent(card_html).lstrip()

        st.markdown(card_html, unsafe_allow_html=True)

    col_idx = (col_idx + 1) % cols_per_row
    if col_idx == 0:
        card_cols = st.columns(cols_per_row)

    st.markdown("---")
    # Download cluster JSON
    cluster_export = {"cluster": cluster_key, "sites": sites, "summary": summary_text}
    st.download_button(f"Download cluster {cluster_key} JSON", data=json.dumps(cluster_export, ensure_ascii=False, indent=2).encode('utf-8'),
                       file_name=f"{username}_cluster_{cluster_key}.json")

# Footer: show raw result file and modification time
mtime = datetime.fromtimestamp(os.path.getmtime(result_file)).isoformat()
st.caption(f"Results file: `{result_file}` — last modified {mtime}")
