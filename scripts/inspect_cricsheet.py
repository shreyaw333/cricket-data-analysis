import requests
from bs4 import BeautifulSoup
import re

def inspect_cricsheet():
    """Inspect the Cricsheet website structure"""
    
    url = "https://cricsheet.org/matches/"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("🔍 INSPECTING CRICSHEET WEBSITE")
        print("=" * 50)
        
        # Check page title
        title = soup.find('title')
        print(f"Page Title: {title.text if title else 'Not found'}")
        
        # Look for different types of links
        all_links = soup.find_all('a', href=True)
        
        json_links = []
        zip_links = []
        other_links = []
        
        for link in all_links:
            href = link['href']
            text = link.get_text(strip=True)
            
            if '.json' in href:
                json_links.append((href, text))
            elif '.zip' in href:
                zip_links.append((href, text))
            elif any(format_name in href.lower() for format_name in ['test', 'odi', 't20', 'ipl']):
                other_links.append((href, text))
        
        print(f"\n📊 LINK ANALYSIS:")
        print(f"Total links found: {len(all_links)}")
        print(f"JSON links: {len(json_links)}")
        print(f"ZIP links: {len(zip_links)}")
        print(f"Format-related links: {len(other_links)}")
        
        # Show some examples
        if json_links:
            print(f"\n📄 JSON Links (first 5):")
            for href, text in json_links[:5]:
                print(f"  • {href} | {text}")
        
        if zip_links:
            print(f"\n📦 ZIP Links (first 5):")
            for href, text in zip_links[:5]:
                print(f"  • {href} | {text}")
        
        if other_links:
            print(f"\n🏏 Format Links (first 10):")
            for href, text in other_links[:10]:
                print(f"  • {href} | {text}")
        
        # Look for specific patterns
        print(f"\n🔍 SEARCHING FOR DOWNLOAD PATTERNS:")
        
        # Check for download sections
        download_sections = soup.find_all(['div', 'section'], class_=re.compile(r'download', re.I))
        if download_sections:
            print(f"Found {len(download_sections)} download sections")
        
        # Check for tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        if tables:
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                print(f"  Table {i+1}: {len(rows)} rows")
                
                # Check first few rows for links
                links_in_table = table.find_all('a', href=True)
                if links_in_table:
                    print(f"    Links in table: {len(links_in_table)}")
                    # Show first link as example
                    first_link = links_in_table[0]
                    print(f"    Example: {first_link['href']} | {first_link.get_text(strip=True)}")
        
        # Save page content for manual inspection
        with open('data/cricsheet_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\n💾 Page content saved to: data/cricsheet_page.html")
        
        return soup
        
    except Exception as e:
        print(f"Error inspecting website: {str(e)}")
        return None

if __name__ == "__main__":
    inspect_cricsheet()