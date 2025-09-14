import streamlit as st

# Configure page
st.set_page_config(
    page_title="Deepsint", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import page modules
from pages.search import show_search_page
from pages.results import show_results_page

# Sidebar navigation
st.sidebar.title("🔍 Deepsint")
st.sidebar.markdown("---")

# Navigation menu
page = st.sidebar.selectbox(
    "Navigate to:",
    ["🔍 Search", "📊 Results"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "Deepsint is an OSINT tool that uses Blackbird to find social media profiles "
    "and processes them through advanced profiling and clustering algorithms."
)

# Main content area
if page == "🔍 Search":
    show_search_page()
elif page == "📊 Results":
    show_results_page()
