from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import requests
from urllib.parse import urljoin
import json

class CricsheetScraper:
    def __init__(self, download_dir="data/raw_json"):
        self.download_dir = download_dir
        self.base_url = "https://cricsheet.org/matches/"
        self.driver = None
        self.setup_driver()
        
        # Create download directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Set download preferences
        prefs = {
            "download.default_directory": os.path.abspath(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def get_match_links_by_format(self, match_format):
        """
        Get all JSON download links for a specific format
        match_format: 'test', 'odi', 't20', 'ipl'
        """
        format_urls = {
            'test': f"{self.base_url}test/",
            'odi': f"{self.base_url}odi/",
            't20': f"{self.base_url}t20/",
            'ipl': f"{self.base_url}ipl/"
        }
        
        if match_format not in format_urls:
            raise ValueError(f"Invalid format: {match_format}")
        
        print(f"Scraping {match_format.upper()} matches...")
        self.driver.get(format_urls[match_format])
        
        # Wait for page to load
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # Find all JSON download links
        json_links = []
        try:
            # Look for links that end with .json
            links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.json')]")
            
            for link in links:
                href = link.get_attribute('href')
                if href and href.endswith('.json'):
                    json_links.append(href)
            
            print(f"Found {len(json_links)} {match_format.upper()} matches")
            
        except NoSuchElementException:
            print(f"No JSON links found for {match_format}")
        
        return json_links
    
    def download_json_file(self, url, match_format):
        """Download a single JSON file"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract filename from URL
            filename = url.split('/')[-1]
            
            # Create format-specific directory
            format_dir = os.path.join(self.download_dir, match_format)
            os.makedirs(format_dir, exist_ok=True)
            
            # Save file
            filepath = os.path.join(format_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=2)
            
            print(f"Downloaded: {filename}")
            return True
            
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")
            return False
    
    def scrape_format(self, match_format, limit=None):
        """
        Scrape all matches for a specific format
        limit: Maximum number of files to download (for testing)
        """
        json_links = self.get_match_links_by_format(match_format)
        
        if limit:
            json_links = json_links[:limit]
            print(f"Limiting to {limit} files for testing")
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, link in enumerate(json_links, 1):
            print(f"Downloading {i}/{len(json_links)}: ", end="")
            
            if self.download_json_file(link, match_format):
                successful_downloads += 1
            else:
                failed_downloads += 1
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        print(f"\n{match_format.upper()} Summary:")
        print(f"✅ Successful: {successful_downloads}")
        print(f"❌ Failed: {failed_downloads}")
        print(f"📁 Saved to: data/raw_json/{match_format}/")
        
        return successful_downloads, failed_downloads
    
    def scrape_all_formats(self, limit_per_format=5):
        """
        Scrape all match formats
        limit_per_format: Limit files per format for testing
        """
        formats = ['test', 'odi', 't20', 'ipl']
        total_successful = 0
        total_failed = 0
        
        print("🏏 Starting Cricsheet Data Scraping...")
        print("=" * 50)
        
        for match_format in formats:
            try:
                successful, failed = self.scrape_format(match_format, limit=limit_per_format)
                total_successful += successful
                total_failed += failed
                print("-" * 30)
                
            except Exception as e:
                print(f"Error scraping {match_format}: {str(e)}")
                print("-" * 30)
        
        print(f"\n🎯 FINAL SUMMARY:")
        print(f"✅ Total Successful: {total_successful}")
        print(f"❌ Total Failed: {total_failed}")
        print(f"📁 Data saved in: {self.download_dir}")
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

# Test the scraper
if __name__ == "__main__":
    scraper = CricsheetScraper()
    
    try:
        # Test with just 2 files per format first
        scraper.scrape_all_formats(limit_per_format=2)
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Scraping error: {str(e)}")
    finally:
        scraper.close()
        print("Browser closed")