import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import urljoin, urlparse

class SimpleCricsheetScraper:
    def __init__(self, download_dir="data/raw_json"):
        self.download_dir = download_dir
        self.base_url = "https://cricsheet.org/matches/"
        self.session = requests.Session()
        
        # Create download directory
        os.makedirs(download_dir, exist_ok=True)
        
        # Headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page_content(self, url):
        """Get page content using requests"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_json_links(self, html_content, base_url):
        """Extract JSON download links from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        json_links = []
        
        # Find all links that end with .json
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.json'):
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, href)
                json_links.append(full_url)
        
        return json_links
    
    def download_json_file(self, url, match_format):
        """Download a single JSON file"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Extract filename from URL
            filename = os.path.basename(urlparse(url).path)
            if not filename.endswith('.json'):
                filename += '.json'
            
            # Create format-specific directory
            format_dir = os.path.join(self.download_dir, match_format)
            os.makedirs(format_dir, exist_ok=True)
            
            # Save file
            filepath = os.path.join(format_dir, filename)
            
            # Try to parse JSON to ensure it's valid
            json_data = response.json()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            
            print(f"✅ Downloaded: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {url}: {str(e)}")
            return False
    
    def scrape_format(self, match_format, limit=None):
        """Scrape matches for a specific format"""
        format_urls = {
            'test': f"{self.base_url}",  # Main page has test matches
            'odi': f"{self.base_url}",
            't20': f"{self.base_url}",
            'ipl': f"{self.base_url}"
        }
        
        print(f"\n🏏 Scraping {match_format.upper()} matches...")
        
        # Get the main page content
        html_content = self.get_page_content(self.base_url)
        if not html_content:
            return 0, 1
        
        # Extract JSON links
        json_links = self.extract_json_links(html_content, self.base_url)
        
        if not json_links:
            print(f"No JSON links found on main page")
            return 0, 1
        
        # Filter links by format if possible (this might need adjustment)
        if limit:
            json_links = json_links[:limit]
        
        print(f"Found {len(json_links)} JSON files to download")
        
        successful = 0
        failed = 0
        
        for i, link in enumerate(json_links, 1):
            print(f"({i}/{len(json_links)}) ", end="")
            
            if self.download_json_file(link, match_format):
                successful += 1
            else:
                failed += 1
            
            # Be respectful with delays
            time.sleep(1)
        
        print(f"\n📊 {match_format.upper()} Summary: ✅ {successful} | ❌ {failed}")
        return successful, failed
    
    def test_connection(self):
        """Test if we can connect to Cricsheet"""
        print("🔍 Testing connection to Cricsheet...")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            print(f"✅ Connection successful! Status: {response.status_code}")
            
            # Check if we can see some content
            if "cricket" in response.text.lower():
                print("✅ Page content looks correct")
                return True
            else:
                print("⚠️ Page content might be different than expected")
                return False
                
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False

# Alternative: Manual URL list (if scraping fails)
def download_sample_files():
    """Download some sample files directly if scraping doesn't work"""
    
    # Some example direct links (these might need to be updated)
    sample_urls = [
        "https://cricsheet.org/downloads/1298304.json",
        "https://cricsheet.org/downloads/1298299.json", 
        "https://cricsheet.org/downloads/1298295.json"
    ]
    
    print("📥 Downloading sample files directly...")
    
    os.makedirs("data/raw_json/sample", exist_ok=True)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    for i, url in enumerate(sample_urls, 1):
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            filename = f"sample_match_{i}.json"
            filepath = os.path.join("data/raw_json/sample", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=2)
            
            print(f"✅ Downloaded: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to download sample {i}: {str(e)}")
        
        time.sleep(1)

if __name__ == "__main__":
    scraper = SimpleCricsheetScraper()
    
    # Test connection first
    if scraper.test_connection():
        print("\n" + "="*50)
        
        try:
            # Try scraping
            scraper.scrape_format("all", limit=5)
            
        except Exception as e:
            print(f"Scraping failed: {str(e)}")
            print("\nFalling back to direct download...")
            download_sample_files()
    
    else:
        print("\nConnection failed. Trying direct download of sample files...")
        download_sample_files()
    
    print(f"\n📁 Check your files in: data/raw_json/")