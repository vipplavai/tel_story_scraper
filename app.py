import streamlit as st
import subprocess
import json
import os
import time

# Set Page Config
st.set_page_config(page_title="Story Scraper", layout="wide")

# Initialize session state
if "scraped_urls" not in st.session_state:
    st.session_state.scraped_urls = []
if "scraped_data" not in st.session_state:
    st.session_state.scraped_data = []

# Title
st.title("📖 Telugu Story Scraper")

# URL Input
url = st.text_input("Enter Story URL:", "")

# Scrape Button
if st.button("Scrape"):
    if url:
        with st.spinner("Scraping the story... Please wait."):
            # Run scraping script
            result = subprocess.run(
                ["python3", "/home/enma/data/stories_scrape.py", url],
                stderr=subprocess.PIPE,
                text=True
            )

            # Check if the script executed successfully
            if result.returncode == 0:
                try:
                    # Locate the latest JSON file inside 'stories' folder
                    story_files = sorted(
                        [f for f in os.listdir("stories") if f.endswith(".json")],
                        key=lambda x: os.path.getctime(os.path.join("stories", x)),
                        reverse=True
                    )

                    if story_files:
                        latest_story_path = os.path.join("stories", story_files[0])

                        # Wait a bit to ensure file is written completely
                        time.sleep(1)

                        # Read the JSON data from the saved file
                        with open(latest_story_path, "r", encoding="utf-8") as f:
                            scraped_story = json.load(f)

                        # Store results in session state
                        st.session_state.scraped_urls.append(url)
                        st.session_state.scraped_data.append(scraped_story)

                        # Update counter
                        st.sidebar.metric(label="URLs Scraped", value=len(st.session_state.scraped_urls))

                        st.success(f"Story Scraped Successfully: {scraped_story['Title']}")
                    else:
                        st.error("No JSON file found after scraping.")

                except json.JSONDecodeError as json_error:
                    st.error(f"Failed to parse scraped story. JSON file might be incomplete.")
            else:
                st.error(f"Scraping failed. Error: {result.stderr}")
    else:
        st.warning("Please enter a valid URL.")

# Display Scraped Stories
st.subheader("📝 Scraped Stories:")
if st.session_state.scraped_data:
    for story in st.session_state.scraped_data:
        with st.expander(story["Title"]):
            st.write(f"**URL:** {story['URL/Href']}")
            st.write(f"**Category:** {story['Category']}")
            st.write(f"**Content:** {story['Content'][:500]}...")  # Show first 500 chars

# Scrape Counter (Top Right)
st.sidebar.header("📊 Scraping Stats")
st.sidebar.metric(label="URLs Scraped", value=len(st.session_state.scraped_urls))

# Download JSON Button
if st.session_state.scraped_data:
    json_filename = "scraped_stories.json"
    json_path = os.path.join("stories", json_filename)

    # Save all scraped stories into a JSON file
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(st.session_state.scraped_data, json_file, ensure_ascii=False, indent=4)

    with open(json_path, "rb") as f:
        st.sidebar.download_button("📥 Download JSON", f, file_name=json_filename, mime="application/json")
