import os
import json
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Directory for temporary storage
TEMP_DIR = "/tmp/stories"

# Ensure TEMP_DIR exists
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

# Function to scrape a story
def scrape_story(url, username):
    # Setup Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        # Extract Title
        title_element = driver.find_element(By.CSS_SELECTOR, "h2.title-target.text-left.d-none.d-sm-block")
        title = title_element.text.strip()

        # Extract Content
        content_div = driver.find_element(By.CSS_SELECTOR, "div.content-container.avoid-text-copy.story")
        paragraphs = content_div.find_elements(By.TAG_NAME, "p")
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

        print(f"Story saved successfully: {json_path}")
        return json_path  # Return file path for retrieval

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

    finally:
        driver.quit()


# If script is run directly with URL and username arguments
if __name__ == "__main__":
    if len(sys.argv) > 2:
        url = sys.argv[1]
        username = sys.argv[2]
        cleanup_old_files()  # Delete old files before saving new one
        scraped_file = scrape_story(url, username)
        if scraped_file:
            print(json.dumps({"file_path": scraped_file}))
