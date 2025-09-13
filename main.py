import streamlit as st

st.set_page_config(page_title="OSINT Visualizer", layout="wide")
st.title("🔍 OSINT Visualizer")

# --- Username Input Form ---
with st.form(key="username_form"):
    username = st.text_input("Enter a username or email:", placeholder="e.g., alice123")
    submitted = st.form_submit_button("Search")

# --- Process Form Submission ---
if submitted:
    if username.strip() == "":
        st.error("Please enter a valid username or email.")
    else:
        st.success(f"Searching for username: {username}")
        # Placeholder for your OSINT logic
        st.write("Here you can trigger Blackbird, Cohere, or other analysis.")
