import os
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_story(url):
    # Set up Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver
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
            "Category": "stories"
        }

        # Create "stories" directory if it doesn't exist
        os.makedirs("stories", exist_ok=True)

        # Save to JSON file
        json_filename = f"stories/{title.replace(' ', '_').replace('/', '_')}.json"
        with open(json_filename, "w", encoding="utf-8") as json_file:
            json.dump(story_data, json_file, ensure_ascii=False, indent=4)

        print(f"Story saved successfully: {json_filename}")

        return story_data  # Return the scraped data for Streamlit

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

    finally:
        driver.quit()


# If script is run directly with an argument (URL)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        scraped_data = scrape_story(url)
        if scraped_data:
            print(json.dumps(scraped_data, ensure_ascii=False, indent=4))
