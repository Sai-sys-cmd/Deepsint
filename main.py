import streamlit as st
import subprocess
import os
import datetime
import json
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
import traceback
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Deepsint Visualizer", layout="wide")
st.title("🔍 Deepsint Visualizer")

# helper: run an async coroutine in a fresh event loop inside a thread
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor

def run_coro_in_thread(coro):
    """
    Run `coro` on a fresh event loop in a worker thread that supports subprocesses on Windows.
    Returns whatever the coroutine returns or raises the exception.
    """
    def _runner():
        # On Windows we need a Proactor event loop policy so subprocesses work.
        if sys.platform == "win32":
            # Set the policy in this thread before creating a loop.
            # It's safe to call multiple times, and we do it inside the worker thread.
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            # cleanup
            try:
                # attempt to cancel pending tasks (if any)
                for task in asyncio.all_tasks(loop):
                    task.cancel()
            except Exception:
                pass
            loop.close()

    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(_runner)
        return fut.result()
    



# --- Username Input Form ---
with st.form(key="username_form"):
    username = st.text_input("Enter a name or username:", placeholder="e.g., alice123")
    submitted = st.form_submit_button("Search")

if submitted:
    if username.strip() == "":
        st.error("Please enter a valid name or username.")
    else:
        st.success(f"Searching for username: {username}")
        

        # Set the PYTHONIOENCODING environment variable to UTF-8 for subprocess
        os.environ["PYTHONIOENCODING"] = "utf-8"

        # Assemble blackbird command (adjust path if needed)
        command = [
            "python", "blackbird/blackbird.py",
            "--username", username,
            "--json"
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=500,
                encoding='utf-8'
            )
            if result.returncode == 0:
                st.info("Blackbird ran successfully and produced JSON.")
            else:
                st.error(f"Blackbird failed:\n{result.stderr}")
                # stop here if blackbird failed
                st.stop()

        except subprocess.TimeoutExpired:
            st.error("The blackbird command timed out. Please try again.")
            st.stop()

        except Exception as e:
            st.error(f"Error running blackbird: {e}")
            st.stop()

        #Determine expected blackbird result path (try robustly)
        current_date = datetime.datetime.now().strftime("%m_%d_%Y")
        blackbird_json_folder = f"blackbird/results/{username}_{current_date}_blackbird"
        #If blackbird writes a different naming pattern, try to find a json file
        blackbird_json_path = os.path.join(
            blackbird_json_folder,
            f"{username}_{current_date}_blackbird.json"
        )
        profile_links = []
        with open(blackbird_json_path, 'r+',encoding='utf-8') as f:
            data = json.load(f)
            for i in range(len(data)):
                # if data[i]["scrape_status"] == "ok":
                profile_links.append(data[i]["url"])

        if len(profile_links)==0:
            st.stop()
        st.write(f"Found {len(profile_links)} profile links. Launching processing pipeline...")

        # import here so app imports even if processing.main is heavy
        from processing.main import findProfiles

        # run the async pipeline in a thread with a fresh loop
        with st.spinner("Processing profiles through pipeline (this may take seconds to minutes)..."):
            try:
                info = run_coro_in_thread(findProfiles(profile_links, username))
                # info should be the dict returned by findProfiles
                results_fname = f"data/results/results_{username}.json"
                with open(results_fname, "w", encoding="utf-8") as fh:
                    json.dump(info, fh, ensure_ascii=False, indent=2)
                    
                st.success("Processing complete — results saved.")
                st.write("Open the **Results** page from the left sidebar to view a pretty visualization of clusters.")

                if info:
                    st.success("Processing complete!")
                    st.subheader("Profile clusters & summaries")
                    st.json(info)  # display nicely
                else:
                    st.info("Processing completed but returned no results.")

            except Exception as exc:
                st.error("Error while processing profiles:")
                # show traceback for debugging
                tb = traceback.format_exc()
                st.code(tb)
        #Need better display of json
        # optional cleanup: remove blackbird folder if you want
        # NOTE: uncomment carefully, only if you want to delete files
        # try:
        shutil.rmtree(blackbird_json_folder)
        # except Exception:
        #     pass
        # ---------- Results UI & navigation helpers (add to your Streamlit app) ----------
       