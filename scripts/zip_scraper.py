import requests
import zipfile
import json
import os
import time
from urllib.parse import urljoin

class CricsheetZipScraper:
    def __init__(self, download_dir="data/raw_json"):
        self.download_dir = download_dir
        self.base_url = "https://cricsheet.org"
        self.session = requests.Session()
        
        # Create directories
        os.makedirs(download_dir, exist_ok=True)
        os.makedirs("data/downloads", exist_ok=True)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def download_and_extract_zip(self, zip_url, format_name):
        """Download ZIP file and extract JSON files"""
        
        print(f"\n🏏 Downloading {format_name} matches...")
        print(f"URL: {zip_url}")
        
        try:
            # Download ZIP file
            response = self.session.get(zip_url, timeout=60)
            response.raise_for_status()
            
            # Save ZIP temporarily
            zip_path = f"data/downloads/{format_name}.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded ZIP: {len(response.content)} bytes")
            
            # Extract JSON files
            format_dir = os.path.join(self.download_dir, format_name)
            os.makedirs(format_dir, exist_ok=True)
            
            extracted_count = 0
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # List all files in ZIP
                file_list = zip_ref.namelist()
                json_files = [f for f in file_list if f.endswith('.json')]
                
                print(f"📦 ZIP contains {len(json_files)} JSON files")
                
                # Extract JSON files (limit for testing)
                for i, json_file in enumerate(json_files[:10]):  # Limit to first 10 for testing
                    try:
                        # Extract file content
                        with zip_ref.open(json_file) as file:
                            json_data = json.load(file)
                        
                        # Save to format directory
                        filename = os.path.basename(json_file)
                        output_path = os.path.join(format_dir, filename)
                        
                        with open(output_path, 'w', encoding='utf-8') as f:
                            json.dump(json_data, f, indent=2)
                        
                        print(f"  ✅ Extracted: {filename}")
                        extracted_count += 1
                        
                    except Exception as e:
                        print(f"  ❌ Failed to extract {json_file}: {str(e)}")
            
            # Clean up ZIP file
            os.remove(zip_path)
            
            print(f"📊 {format_name} Summary: {extracted_count} files extracted")
            return extracted_count
            
        except Exception as e:
            print(f"❌ Error downloading/extracting {format_name}: {str(e)}")
            return 0
    
    def download_all_formats(self):
        """Download all cricket formats"""
        
        # ZIP URLs from the inspection
        zip_urls = {
            'tests': f"{self.base_url}/downloads/tests_json.zip",
            'odis': f"{self.base_url}/downloads/odis_json.zip", 
            't20s': f"{self.base_url}/downloads/t20s_json.zip",
            'ipl': f"{self.base_url}/downloads/ipl_json.zip"
        }
        
        print("🏏 CRICSHEET DATA DOWNLOAD")
        print("=" * 50)
        
        total_files = 0
        
        for format_name, zip_url in zip_urls.items():
            try:
                files_extracted = self.download_and_extract_zip(zip_url, format_name)
                total_files += files_extracted
                
                print("-" * 30)
                time.sleep(2)  # Be respectful between downloads
                
            except Exception as e:
                print(f"❌ Failed to process {format_name}: {str(e)}")
                print("-" * 30)
        
        print(f"\n🎯 FINAL SUMMARY:")
        print(f"✅ Total files extracted: {total_files}")
        print(f"📁 Files saved in: {self.download_dir}")
        
        # Show directory structure
        self.show_directory_structure()
        
        return total_files
    
    def show_directory_structure(self):
        """Show what we downloaded"""
        print(f"\n📂 DIRECTORY STRUCTURE:")
        
        for root, dirs, files in os.walk(self.download_dir):
            level = root.replace(self.download_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show first 5 files
                print(f"{subindent}{file}")
            
            if len(files) > 5:
                print(f"{subindent}... and {len(files) - 5} more files")

if __name__ == "__main__":
    scraper = CricsheetZipScraper()
    
    try:
        total_files = scraper.download_all_formats()
        
        if total_files > 0:
            print(f"\n🎉 SUCCESS! Ready to proceed with data processing.")
        else:
            print(f"\n⚠️ No files downloaded. Creating sample data...")
            # Fall back to sample data creation
            exec(open('scripts/create_sample_data.py').read())
            
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
    except Exception as e:
        print(f"Download error: {str(e)}")