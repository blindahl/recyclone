"""
Arc Raiders Recycling Tracker - Web Scraper Module
"""
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Callable, Any
import requests
import time
import logging
import json
import os
from bs4 import BeautifulSoup
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def retry_with_backoff(max_retries: int = 3, backoff_delays: List[float] = [1.0, 2.0, 4.0]):
    """
    Decorator to retry a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_delays: List of delays (in seconds) between retries
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(__name__)
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries:
                        delay = backoff_delays[attempt] if attempt < len(backoff_delays) else backoff_delays[-1]
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} retry attempts failed for {func.__name__}")
                        raise
            
        return wrapper
    return decorator


@dataclass
class Material:
    """Represents a material obtained from recycling an item."""
    name: str
    quantity: int


@dataclass
class Item:
    """Represents a game item that can be recycled."""
    name: str
    category: str
    url: str
    materials: List[Material]
    
    def to_dict(self):
        """Convert Item to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'category': self.category,
            'url': self.url,
            'materials': [asdict(m) for m in self.materials]
        }


class WikiScraper:
    """Scrapes item recycling data from the Arc Raiders wiki."""
    
    CATEGORIES = {
        'Weapons': 'https://arcraiders.wiki/wiki/Weapons',
        'Augments': 'https://arcraiders.wiki/wiki/Augments',
        'Shields': 'https://arcraiders.wiki/wiki/Shields',
        'Healing': 'https://arcraiders.wiki/wiki/Healing',
        'Quick Use': 'https://arcraiders.wiki/wiki/Quick_Use',
        'Grenades': 'https://arcraiders.wiki/wiki/Grenades',
        'Traps': 'https://arcraiders.wiki/wiki/Traps'
    }
    
    def __init__(self, base_url: str = "https://arcraiders.wiki", 
                 api_endpoint: str = "/api.php",
                 rate_limit: float = 1.0):
        """
        Initialize the WikiScraper.
        
        Args:
            base_url: Base URL of the wiki
            api_endpoint: Path to the MediaWiki API endpoint
            rate_limit: Minimum seconds between requests (default: 1.0)
        """
        self.base_url = base_url
        self.api_url = base_url + api_endpoint
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
        # Set up requests session with connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ArcRaidersRecyclingTracker/1.0'
        })
        
        self.logger = logging.getLogger(__name__)
        
        # Track failures for reporting
        self.failed_categories = []
        self.failed_items = []
    
    def _rate_limit_wait(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()
    
    def scrape_category(self, category_name: str, category_url: str) -> List[Dict]:
        """
        Scrape a category page to extract item links.
        Handles errors gracefully and continues processing.
        
        Args:
            category_name: Name of the category
            category_url: URL of the category page
            
        Returns:
            List of dictionaries with item names and URLs
        """
        self.logger.info(f"Scraping category: {category_name}")
        
        try:
            return self._scrape_category_with_retry(category_name, category_url)
        except Exception as e:
            self.logger.error(f"Failed to scrape category {category_name} after retries: {e}")
            self.failed_categories.append({'name': category_name, 'url': category_url, 'error': str(e)})
            return []
    
    @retry_with_backoff(max_retries=3, backoff_delays=[1.0, 2.0, 4.0])
    def _scrape_category_with_retry(self, category_name: str, category_url: str) -> List[Dict]:
        """Internal method with retry logic for category scraping."""
        self._rate_limit_wait()
        
        response = self.session.get(category_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        item_links = []
        
        # Find all links in the page content
        # MediaWiki typically uses div with class 'mw-parser-output' for content
        content_div = soup.find('div', class_='mw-parser-output')
        if not content_div:
            content_div = soup
        
        # Extract links that are likely item pages
        # Exclude special pages, categories, and navigation links
        seen_urls = set()
        for link in content_div.find_all('a', href=True):
            href = link['href']
            
            # Skip non-wiki links, special pages, and anchors
            if not href.startswith('/wiki/') or ':' in href or '#' in href:
                continue
            
            # Skip the category page itself
            if href == category_url.replace(self.base_url, ''):
                continue
            
            full_url = self.base_url + href if href.startswith('/') else href
            
            # Avoid duplicates
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            
            item_name = link.get_text(strip=True)
            if item_name:
                item_links.append({
                    'name': item_name,
                    'url': full_url,
                    'category': category_name
                })
        
        self.logger.info(f"Found {len(item_links)} items in {category_name}")
        return item_links
    
    def extract_recycling_data(self, html_content: str) -> List[Material]:
        """
        Extract recycling materials from HTML content.
        
        Args:
            html_content: HTML content of an item page
            
        Returns:
            List of Material objects
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        materials = []
        
        # Look for the "Recycled & Salvaged Materials" section
        # This could be in various formats - heading, table, list, etc.
        
        # Try to find a heading with this text
        recycling_heading = None
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text(strip=True).lower()
            if 'recycled' in heading_text and 'salvaged' in heading_text:
                recycling_heading = heading
                break
        
        if not recycling_heading:
            return materials
        
        # Get content after the heading until the next heading
        current = recycling_heading.find_next_sibling()
        
        while current and current.name not in ['h2', 'h3', 'h4']:
            # Check if it's a table
            if current.name == 'table':
                materials.extend(self._extract_from_table(current))
            # Check if it's a list
            elif current.name in ['ul', 'ol']:
                materials.extend(self._extract_from_list(current))
            # Check if it's a div or paragraph with text
            elif current.name in ['div', 'p']:
                materials.extend(self._extract_from_text(current))
            
            current = current.find_next_sibling()
        
        return materials
    
    def _extract_from_table(self, table) -> List[Material]:
        """Extract materials from a table element."""
        materials = []
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                material_name = cells[0].get_text(strip=True)
                quantity_text = cells[1].get_text(strip=True)
                
                # Extract numeric quantity
                quantity = self._parse_quantity(quantity_text)
                if material_name and quantity is not None:
                    materials.append(Material(name=material_name, quantity=quantity))
        
        return materials
    
    def _extract_from_list(self, list_element) -> List[Material]:
        """Extract materials from a list element."""
        materials = []
        items = list_element.find_all('li')
        
        for item in items:
            text = item.get_text(strip=True)
            # Try to parse format like "Material Name: 5" or "Material Name (5)"
            material, quantity = self._parse_material_text(text)
            if material and quantity is not None:
                materials.append(Material(name=material, quantity=quantity))
        
        return materials
    
    def _extract_from_text(self, element) -> List[Material]:
        """Extract materials from text content."""
        materials = []
        text = element.get_text(strip=True)
        
        # Split by common delimiters
        for line in text.split('\n'):
            material, quantity = self._parse_material_text(line)
            if material and quantity is not None:
                materials.append(Material(name=material, quantity=quantity))
        
        return materials
    
    def _parse_material_text(self, text: str) -> tuple:
        """
        Parse material name and quantity from text.
        
        Returns:
            Tuple of (material_name, quantity) or (None, None)
        """
        import re
        
        # Try patterns like "Material: 5", "Material (5)", "Material x5", "5x Material"
        patterns = [
            r'(.+?):\s*(\d+)',           # Material: 5
            r'(.+?)\s*\((\d+)\)',        # Material (5)
            r'(.+?)\s*x\s*(\d+)',        # Material x5
            r'(\d+)\s*x\s*(.+)',         # 5x Material
            r'(.+?)\s*-\s*(\d+)',        # Material - 5
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if pattern == r'(\d+)\s*x\s*(.+)':
                    # Quantity comes first
                    return groups[1].strip(), int(groups[0])
                else:
                    return groups[0].strip(), int(groups[1])
        
        return None, None
    
    def _parse_quantity(self, text: str) -> int:
        """Extract numeric quantity from text."""
        import re
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else None
    
    def scrape_item_page(self, item_info: Dict) -> Item:
        """
        Scrape an individual item page for recycling data.
        Handles errors gracefully and returns item with empty materials on failure.
        
        Args:
            item_info: Dictionary with 'name', 'url', and 'category'
            
        Returns:
            Item object with recycling materials (empty list if scraping fails)
        """
        self.logger.info(f"Scraping item: {item_info['name']}")
        
        try:
            return self._scrape_item_with_retry(item_info)
        except Exception as e:
            self.logger.error(f"Failed to scrape item {item_info['name']} after retries: {e}")
            self.failed_items.append({'name': item_info['name'], 'url': item_info['url'], 'error': str(e)})
            # Return item with empty materials on error
            return Item(
                name=item_info['name'],
                category=item_info['category'],
                url=item_info['url'],
                materials=[]
            )
    
    @retry_with_backoff(max_retries=3, backoff_delays=[1.0, 2.0, 4.0])
    def _scrape_item_with_retry(self, item_info: Dict) -> Item:
        """Internal method with retry logic for item scraping."""
        self._rate_limit_wait()
        
        response = self.session.get(item_info['url'], timeout=30)
        response.raise_for_status()
        
        materials = self.extract_recycling_data(response.text)
        
        return Item(
            name=item_info['name'],
            category=item_info['category'],
            url=item_info['url'],
            materials=materials
        )
    
    def scrape_all_categories(self) -> Dict:
        """
        Scrape all item categories and their recycling data.
        
        Returns:
            Dictionary with categories as keys and lists of items as values
        """
        self.logger.info("Starting scrape of all categories")
        start_time = time.time()
        
        # Reset failure tracking
        self.failed_categories = []
        self.failed_items = []
        
        all_data = {'categories': {}}
        total_items = 0
        
        # Scrape each category
        for category_name, category_url in self.CATEGORIES.items():
            # Get item links from category page
            item_links = self.scrape_category(category_name, category_url)
            
            # Scrape each item page
            items = []
            for item_info in item_links:
                item = self.scrape_item_page(item_info)
                items.append(item)
                total_items += 1
            
            all_data['categories'][category_name] = [item.to_dict() for item in items]
        
        # Add metadata
        elapsed_time = time.time() - start_time
        all_data['metadata'] = {
            'version': '1.0',
            'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'total_items': total_items,
            'categories_count': len(self.CATEGORIES),
            'elapsed_seconds': round(elapsed_time, 2),
            'failed_categories': len(self.failed_categories),
            'failed_items': len(self.failed_items)
        }
        
        # Log summary
        self.logger.info(f"Scraping complete in {elapsed_time:.2f}s")
        self.logger.info(f"Total items: {total_items}")
        self.logger.info(f"Failed categories: {len(self.failed_categories)}")
        self.logger.info(f"Failed items: {len(self.failed_items)}")
        
        if self.failed_categories:
            self.logger.warning(f"Failed categories: {[c['name'] for c in self.failed_categories]}")
        if self.failed_items:
            self.logger.warning(f"Failed items: {[i['name'] for i in self.failed_items]}")
        
        return all_data
    
    def save_to_json(self, data: Dict, filepath: str) -> None:
        """
        Save scraped data to JSON file with atomic write.
        
        Args:
            data: Dictionary containing scraped data
            filepath: Path to save the JSON file
        """
        self.logger.info(f"Saving data to {filepath}")
        
        try:
            # Ensure directory exists
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Use atomic write: write to temp file, then rename
            temp_filepath = filepath + '.tmp'
            
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(temp_filepath, filepath)
            
            self.logger.info(f"Successfully saved data to {filepath}")
            
        except PermissionError as e:
            self.logger.error(f"Permission denied when writing to {filepath}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error saving JSON file: {e}")
            # Clean up temp file if it exists
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except:
                    pass
            raise


if __name__ == "__main__":
    pass
