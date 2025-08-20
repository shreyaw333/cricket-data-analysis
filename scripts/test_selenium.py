from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

def test_selenium():
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # For macOS ARM64, specify the correct driver
        service = Service(ChromeDriverManager().install())
        
        # Create driver with options
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test navigation
        driver.get("https://cricsheet.org/matches/")
        print("Page title:", driver.title)
        print("Selenium setup successful!")
        
        driver.quit()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying alternative setup...")
        
        # Alternative: Try without webdriver-manager
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://cricsheet.org/matches/")
            print("Page title:", driver.title)
            print("Alternative setup successful!")
            driver.quit()
            
        except Exception as e2:
            print(f"Alternative also failed: {e2}")
            print("\nPlease install ChromeDriver manually:")
            print("1. Download from: https://chromedriver.chromium.org/")
            print("2. Extract and place in /usr/local/bin/")

if __name__ == "__main__":
    test_selenium()