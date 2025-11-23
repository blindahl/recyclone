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

    def scrape_loot(self, loot_url: str = None) -> Dict:
        """
        Scrape the Loot page to extract all loot item links and their
        recycling and salvaging results.

        Returns a dictionary in the same overall shape as scrape_all_categories
        so it can be saved to JSON and used by the HTML generator.
        """
        if loot_url is None:
            loot_url = self.base_url + '/wiki/Loot'

        self.logger.info(f"Scraping Loot page: {loot_url}")
        start_time = time.time()

        all_items = []
        try:
            self._rate_limit_wait()
            resp = self.session.get(loot_url, timeout=30)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.content, 'html.parser')
            content_div = soup.find('div', class_='mw-parser-output') or soup

            # Find the first table on the Loot page (items are often listed in a table)
            table = content_div.find('table')
            link_candidates = []

            if table:
                self.logger.info('Found a table on Loot page; extracting rows')
                rows = table.find_all('tr')
                # Skip header row(s)
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if not cols:
                        continue

                    # Try to find a link to the item in the first column
                    link = cols[0].find('a', href=True)
                    if not link:
                        continue

                    href = link['href']
                    if not href.startswith('/wiki/'):
                        continue

                    link_candidates.append(link)
            else:
                # Fallback: scan the content area for wiki links that look like items
                self.logger.warning('No table found on Loot page — falling back to scanning for links')
                seen = set()
                for link in content_div.find_all('a', href=True):
                    href = link['href']
                    # Skip non-wiki links, special pages, and anchors
                    if not href.startswith('/wiki/') or ':' in href or '#' in href:
                        continue
                    if href in seen:
                        continue
                    seen.add(href)
                    link_candidates.append(link)

            # Iterate over candidate links and scrape each item page
            for link in link_candidates:
                href = link['href']
                full_url = self.base_url + href if href.startswith('/') else href
                item_name = link.get_text(strip=True) or full_url

                item_info = {
                    'name': item_name,
                    'category': 'Loot',
                    'url': full_url
                }

                # Scrape the individual item page for recycling and salvaging
                try:
                    self.logger.info(f"Scraping loot item link: {item_name}")
                    item = self._scrape_loot_item(item_info)
                    all_items.append(item)
                except Exception as e:
                    self.logger.warning(f"Failed to scrape item {item_name}: {e}")
                    self.failed_items.append({'name': item_name, 'url': full_url, 'error': str(e)})

            elapsed = time.time() - start_time
            result = {
                'categories': {'Loot': [item.to_dict() for item in all_items]},
                'metadata': {
                    'version': '1.0',
                    'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    'total_items': len(all_items),
                    'categories_count': 1,
                    'elapsed_seconds': round(elapsed, 2),
                    'failed_categories': len(self.failed_categories),
                    'failed_items': len(self.failed_items)
                }
            }

            self.logger.info(f"Scraped {len(all_items)} loot items in {elapsed:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Failed to scrape Loot page: {e}")
            raise

    def _scrape_loot_item(self, item_info: Dict) -> Item:
        """
        Scrape a single loot item page and extract both Recycling and Salvaging
        results. Returns an Item object where the `materials` field is a
        flattened list combining recycling and salvaging entries with an
        extra attribute in their names to differentiate source.
        """
        self._rate_limit_wait()
        resp = self.session.get(item_info['url'], timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Extract recycling and salvaging sections separately
        recycling_materials = self._extract_section_materials(soup, ['recycling', 'recycled', 'recycling results'])
        salvaging_materials = self._extract_section_materials(soup, ['salvaging', 'salvaged', 'salvaging results'])

        # Compose materials list with clear naming so the generator can
        # display both recycling and salvaging results per item.
        materials = []
        for m in recycling_materials:
            materials.append(Material(name=m.name, quantity=m.quantity))
        for m in salvaging_materials:
            # To allow the front-end to separate salvaging from recycling
            # we'll prefix the material name with "(Salvage) " so both types
            # are preserved. The generator will also be compatible if the
            # data contains structured 'recycling'/'salvaging' keys instead.
            materials.append(Material(name=f"(Salvage) {m.name}", quantity=m.quantity))

        return Item(name=item_info['name'], category=item_info['category'], url=item_info['url'], materials=materials)

    def _extract_section_materials(self, soup, keywords: List[str]) -> List[Material]:
        """
        Find a section heading matching any of the given keywords and extract
        materials using existing helpers. Returns a list of Material objects.
        """
        heading = None
        for h in soup.find_all(['h2', 'h3', 'h4']):
            text = h.get_text(strip=True).lower()
            for kw in keywords:
                if kw in text:
                    heading = h
                    break
            if heading:
                break

        if not heading:
            return []

        import re
        materials: List[Material] = []

        # Walk forward through the document from the heading. Some pages
        # wrap the section content in a <section>/<div> or other container
        # rather than as direct siblings, so using find_next() is more
        # robust than find_next_sibling(). Stop when the next heading is
        # encountered.
        node = heading
        while True:
            node = node.find_next()
            if node is None:
                break
            # stop when we hit another section heading
            if getattr(node, 'name', None) in ['h2', 'h3', 'h4']:
                break

            if getattr(node, 'name', None) == 'table':
                # Special handling: some pages use a table with columns:
                # Item | → | Recycling results | Salvaging results
                # In that case we want to extract the recycling or salvaging
                # cell contents rather than treating the first two columns as
                # material/quantity rows.
                try:
                    rows = node.find_all('tr')
                    if not rows:
                        continue
                    header_cells = [c.get_text(strip=True).lower() for c in rows[0].find_all(['th', 'td'])]
                    # look for recycling/salvaging column indices
                    recycling_idx = None
                    salvaging_idx = None
                    for idx, htxt in enumerate(header_cells):
                        if 'recycling' in htxt:
                            recycling_idx = idx
                        if 'salvag' in htxt:
                            salvaging_idx = idx

                    if recycling_idx is not None or salvaging_idx is not None:
                        # Determine which column(s) we're interested in based on
                        # the keywords passed to this function. The caller
                        # typically calls this for recycling and salvaging
                        # separately.
                        want_recycling = any('recycl' in kw for kw in keywords)
                        want_salvaging = any('salvag' in kw for kw in keywords)
                        # iterate data rows
                        for row in rows[1:]:
                            cells = row.find_all(['td', 'th'])
                            # parse recycling cell(s)
                            if recycling_idx is not None and recycling_idx < len(cells) and (want_recycling or not want_salvaging):
                                cell_text = cells[recycling_idx].get_text(" ", strip=True)
                                # split on common delimiters (commas, semicolons or newlines)
                                parts = [p.strip() for p in re.split('[,;/\\n]+', cell_text) if p.strip()]
                                for part in parts:
                                    part_norm = part.replace('×', 'x')
                                    mat, qty = self._parse_material_text(part_norm)
                                    if mat and qty is not None:
                                        materials.append(Material(name=mat, quantity=qty))
                            # parse salvaging cell(s)
                            if salvaging_idx is not None and salvaging_idx < len(cells) and (want_salvaging or not want_recycling):
                                cell_text = cells[salvaging_idx].get_text(" ", strip=True)
                                parts = [p.strip() for p in re.split('[,;/\\n]+', cell_text) if p.strip()]
                                for part in parts:
                                    part_norm = part.replace('×', 'x')
                                    mat, qty = self._parse_material_text(part_norm)
                                    if mat and qty is not None:
                                        materials.append(Material(name=mat, quantity=qty))
                        # we've processed the table — return results to avoid
                        # accidentally parsing unrelated footer text later on
                        return materials
                except Exception:
                    # fallback to generic table extractor on errors
                    materials.extend(self._extract_from_table(node))
            elif getattr(node, 'name', None) in ['ul', 'ol']:
                materials.extend(self._extract_from_list(node))
            elif getattr(node, 'name', None) in ['div', 'p', 'section']:
                # If the div/section contains a table or list, extract from
                # those first; otherwise try parsing inline text.
                inner_table = node.find('table')
                if inner_table:
                    materials.extend(self._extract_from_table(inner_table))
                    # continue; there may be more tables/lists further on
                    continue

                inner_list = node.find(['ul', 'ol'])
                if inner_list:
                    materials.extend(self._extract_from_list(inner_list))
                    continue

                # Fall back to extracting text from the node
                materials.extend(self._extract_from_text(node))

        return materials

    def save_to_python_module(self, data: Dict, filepath: str) -> None:
        """
        Save scraped data to a Python module that provides a `RECYCLING_DATA`
        variable. The data is embedded as JSON and parsed at import-time to
        preserve types.
        """
        self.logger.info(f"Saving data to python module {filepath}")
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        json_text = json.dumps(data, ensure_ascii=False, indent=2)
        content = f"import json\nRECYCLING_DATA = json.loads(r'''{json_text}''')\n"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"Successfully wrote python module to {filepath}")
        except Exception as e:
            self.logger.error(f"Error writing python module: {e}")
            raise
    
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
