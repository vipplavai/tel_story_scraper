import os
import json
import sys
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Directory for temporary storage (Render does not allow permanent storage)
TEMP_DIR = "/tmp/stories"
os.makedirs(TEMP_DIR, exist_ok=True)

# Function to delete files older than 24 hours
def cleanup_old_files():
    current_time = time.time()
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > 24 * 3600:  # 24 hours
                os.remove(file_path)

# Function to scrape a story using BeautifulSoup
def scrape_story(url, username):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error: Unable to access {url}")
            return None

        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract Title
        title_element = soup.select_one("h2.title-target.text-left.d-none.d-sm-block")
        title = title_element.text.strip() if title_element else "Untitled"

        # Extract Content (all <p> inside the content-container div)
        content_div = soup.select_one("div.content-container.avoid-text-copy.story")
        paragraphs = content_div.find_all("p") if content_div else []
        content = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])

        # Prepare JSON Data
        story_data = {
            "Title": title,
            "URL/Href": url,
            "Content": content,
            "Category": "stories",
            "Username": username,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to JSON file in /tmp/
        json_filename = f"{title.replace(' ', '_').replace('/', '_')}.json"
        json_path = os.path.join(TEMP_DIR, json_filename)

        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(story_data, json_file, ensure_ascii=False, indent=4)

        print(json.dumps({"file_path": json_path}))  # Output JSON path for app.py to read
        return json_path  # Return file path

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# If script is run directly with URL and username arguments
if __name__ == "__main__":
    if len(sys.argv) > 2:
        url = sys.argv[1]
        username = sys.argv[2]
        cleanup_old_files()  # Delete old files before saving new one
        scrape_story(url, username)
