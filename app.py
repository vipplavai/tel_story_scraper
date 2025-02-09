import streamlit as st
import subprocess
import json
import os
import time
from datetime import datetime

# Set Page Config
st.set_page_config(page_title="Story Scraper", layout="wide")

# Initialize session state
if "scraped_urls" not in st.session_state:
    st.session_state.scraped_urls = []
if "scraped_data" not in st.session_state:
    st.session_state.scraped_data = []
if "username" not in st.session_state:
    st.session_state.username = ""

# Title
st.title("📖 Telugu Story Scraper")

# Ask for Username
username = st.text_input("Enter Your Username:", value=st.session_state.username)
st.session_state.username = username  # Store in session

# URL Input
url = st.text_input("Enter Story URL:", "")

# Scrape Button
if st.button("Scrape"):
    if url and username:
        with st.spinner("Scraping the story... Please wait."):
            # Run scraping script with username argument
            result = subprocess.run(
                ["python3", "/home/enma/data/stories_scrape.py", url, username],
                capture_output=True,
                text=True
            )

            # Check if the script executed successfully
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout.strip())

                    # Read the JSON data from the saved file
                    if "file_path" in response:
                        with open(response["file_path"], "r", encoding="utf-8") as f:
                            scraped_story = json.load(f)

                        # Store results in session state
                        st.session_state.scraped_urls.append(url)
                        st.session_state.scraped_data.append(scraped_story)

                        # Update counter
                        st.sidebar.metric(label="URLs Scraped", value=len(st.session_state.scraped_urls))

                        st.success(f"Story Scraped Successfully: {scraped_story['Title']}")
                    else:
                        st.error("No valid file path returned after scraping.")

                except json.JSONDecodeError as json_error:
                    st.error(f"Failed to parse scraped story. JSON file might be incomplete.")
            else:
                st.error(f"Scraping failed. Error: {result.stderr}")
    else:
        st.warning("Please enter both a username and a valid URL.")

# Display Scraped Stories
st.subheader("📝 Scraped Stories:")
if st.session_state.scraped_data:
    for story in st.session_state.scraped_data:
        with st.expander(story["Title"]):
            st.write(f"**URL:** {story['URL/Href']}")
            st.write(f"**Category:** {story['Category']}")
            st.write(f"**Scraped by:** {story['Username']}")
            st.write(f"**Date:** {story['Date']}")
            st.write(f"**Content:** {story['Content'][:500]}...")  # Show first 500 chars

# Scrape Counter (Top Right)
st.sidebar.header("📊 Scraping Stats")
st.sidebar.metric(label="URLs Scraped", value=len(st.session_state.scraped_urls))

# Download JSON Button
if st.session_state.scraped_data:
    json_filename = f"scraped_stories_{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    json_path = os.path.join("/tmp", json_filename)

    # Save all scraped stories into a JSON file
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(st.session_state.scraped_data, json_file, ensure_ascii=False, indent=4)

    with open(json_path, "rb") as f:
        st.sidebar.download_button("📥 Download JSON", f, file_name=json_filename, mime="application/json")
