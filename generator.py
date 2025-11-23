"""
Arc Raiders Recycling Tracker - HTML Generator Module
"""
import json
import os
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class HTMLGenerator:
    """Generates an interactive HTML page from recycling data."""
    
    def __init__(self, data_filepath: str):
        """
        Initialize the HTMLGenerator.
        
        Args:
            data_filepath: Path to the JSON data file
        """
        self.data_filepath = data_filepath
        self.data = None
        self.logger = logging.getLogger(__name__)
    
    def load_data(self) -> Dict:
        """
        Load and validate JSON data.
        
        Returns:
            Dictionary containing the loaded data
            
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ValueError: If JSON is invalid or doesn't match expected schema
        """
        self.logger.info(f"Loading data from {self.data_filepath}")
        
        if not os.path.exists(self.data_filepath):
            raise FileNotFoundError(
                f"Data file not found: {self.data_filepath}\n"
                f"Please run with --scrape flag to generate the data file."
            )
        
        try:
            with open(self.data_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check version for backward compatibility
            version = data.get('metadata', {}).get('version', '1.0')
            self.logger.info(f"Data file version: {version}")
            
            # Validate schema
            if 'categories' not in data:
                raise ValueError("Invalid JSON: missing 'categories' key")
            
            if not isinstance(data['categories'], dict):
                raise ValueError("Invalid JSON: 'categories' must be a dictionary")
            
            # Validate each category has items
            for category_name, items in data['categories'].items():
                if not isinstance(items, list):
                    raise ValueError(f"Invalid JSON: category '{category_name}' must contain a list of items")
                
                # Validate item structure
                for item in items:
                    if not isinstance(item, dict):
                        raise ValueError(f"Invalid JSON: items must be dictionaries")
                    
                    required_fields = ['name', 'url', 'materials']
                    for field in required_fields:
                        if field not in item:
                            raise ValueError(f"Invalid JSON: item missing required field '{field}'")
                    
                    # Validate materials
                    if not isinstance(item['materials'], list):
                        raise ValueError(f"Invalid JSON: item materials must be a list")
            
            self.data = data
            self.logger.info(f"Successfully loaded data with {data.get('metadata', {}).get('total_items', 0)} items")
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise
    
    def generate_html(self, output_filepath: str) -> None:
        """
        Generate the complete HTML file.
        
        Args:
            output_filepath: Path where the HTML file will be saved
        """
        self.logger.info(f"Generating HTML to {output_filepath}")
        
        if self.data is None:
            self.load_data()
        
        # Build HTML document
        html_parts = []
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html lang="en">')
        html_parts.append('<head>')
        html_parts.append('    <meta charset="UTF-8">')
        html_parts.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_parts.append('    <title>Arc Raiders Recycling Tracker</title>')
        html_parts.append(self.embed_css())
        html_parts.append('</head>')
        html_parts.append('<body>')
        html_parts.append('    <div class="container">')
        html_parts.append('        <h1>Arc Raiders Recycling Tracker</h1>')
        html_parts.append('        <div id="controls">')
        html_parts.append('            <div id="checkboxes">')
        html_parts.append(self.generate_checkboxes_html())
        html_parts.append('            </div>')
        html_parts.append('            <div id="sorting">')
        html_parts.append('                <button id="sort-asc">Sort Ascending ↑</button>')
        html_parts.append('                <button id="sort-desc">Sort Descending ↓</button>')
        html_parts.append('            </div>')
        html_parts.append('        </div>')
        html_parts.append('        <div id="results">')
        html_parts.append(self.generate_table_html())
        html_parts.append('        </div>')
        html_parts.append('    </div>')
        html_parts.append(self.embed_javascript())
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        html_content = '\n'.join(html_parts)
        
        # Write to file
        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"Successfully generated HTML at {output_filepath}")
        except Exception as e:
            self.logger.error(f"Error writing HTML file: {e}")
            raise
    
    def generate_checkboxes_html(self) -> str:
        """
        Generate HTML for material checkboxes.
        
        Returns:
            HTML string containing checkbox elements
        """
        # For the new Loot-based view we don't need per-material checkboxes by
        # default. Keep a small explanatory paragraph instead.
        return '<p>Select sorting buttons below to sort the table by item name, recycling results, or salvaging results.</p>'
    
    def generate_table_html(self) -> str:
        """
        Generate HTML for the items table.
        
        Returns:
            HTML string containing the table structure
        """
        table_html = '''
            <table id="items-table">
                <thead>
                    <tr>
                        <th>Item Name</th>
                        <th>Category</th>
                        <th>Recycling Results</th>
                        <th>Salvaging Results</th>
                    </tr>
                </thead>
                <tbody id="table-body">
                    <tr>
                        <td colspan="4" class="no-data">No data available</td>
                    </tr>
                </tbody>
            </table>'''

        return table_html
    
    def embed_css(self) -> str:
        """
        Generate embedded CSS styles.
        
        Returns:
            HTML style tag with CSS
        """
        css = '''
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        
        #controls {
            margin-bottom: 30px;
        }
        
        #checkboxes {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        
        .checkbox-label {
            display: inline-flex;
            align-items: center;
            padding: 8px 12px;
            background-color: white;
            border: 2px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
            min-height: 44px;
            min-width: 44px;
        }
        
        .checkbox-label:hover {
            border-color: #4CAF50;
            background-color: #f0f8f0;
        }
        
        .checkbox-label input[type="checkbox"] {
            margin-right: 8px;
            cursor: pointer;
            width: 18px;
            height: 18px;
        }
        
        .checkbox-label input[type="checkbox"]:checked + span {
            font-weight: bold;
            color: #4CAF50;
        }
        
        #sorting {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
        
        button {
            padding: 12px 24px;
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
            min-height: 44px;
            min-width: 44px;
        }
        
        button:hover {
            background-color: #45a049;
        }
        
        button:active {
            background-color: #3d8b40;
        }
        
        #results {
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
        }
        
        tr:hover {
            background-color: #f5f5f5;
        }
        
        .no-data {
            text-align: center;
            color: #999;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            #checkboxes {
                padding: 10px;
            }
            
            .checkbox-label {
                font-size: 14px;
                padding: 6px 10px;
            }
            
            button {
                padding: 10px 16px;
                font-size: 14px;
            }
            
            th, td {
                padding: 8px;
                font-size: 14px;
            }
        }
    </style>'''
        
        return css
    
    def embed_javascript(self) -> str:
        """
        Generate embedded JavaScript for interactivity.
        
        Returns:
            HTML script tag with JavaScript
        """
        # Embed the data as JSON for JavaScript to use
        data_json = json.dumps(self.data)

        js = f'''
    <script>
        // Embedded data
        const recyclingData = {data_json};

        const tableBody = document.getElementById('table-body');

        // Build a flat list of items with separate recycling/salvaging lists
        function buildItems() {{
            const items = [];
            Object.keys(recyclingData.categories).forEach(category => {{
                recyclingData.categories[category].forEach(item => {{
                    const recycling = [];
                    const salvaging = [];
                    (item.materials || []).forEach(m => {{
                        if (m.name && m.name.startsWith('(Salvage)')) {{
                            const name = m.name.replace('(Salvage) ', '').trim();
                            salvaging.push({{name: name, quantity: m.quantity}});
                        }} else {{
                            recycling.push({{name: m.name, quantity: m.quantity}});
                        }}
                    }});

                    const recyclingTotal = recycling.reduce((s, x) => s + (x.quantity || 0), 0);
                    const salvagingTotal = salvaging.reduce((s, x) => s + (x.quantity || 0), 0);

                    items.push({{
                        name: item.name,
                        category: category,
                        url: item.url,
                        recycling: recycling,
                        salvaging: salvaging,
                        recyclingTotal: recyclingTotal,
                        salvagingTotal: salvagingTotal
                    }});
                }});
            }});
            return items;
        }}

        function renderTable(items) {{
            tableBody.innerHTML = '';
            if (!items || items.length === 0) {{
                const row = document.createElement('tr');
                row.innerHTML = '<td colspan="4" class="no-data">No items found</td>';
                tableBody.appendChild(row);
                return;
            }}

            items.forEach(item => {{
                const row = document.createElement('tr');
                const recyclingText = item.recycling.map(r => `${{escapeHtml(r.name)}} x${{r.quantity}}`).join(', ');
                const salvagingText = item.salvaging.map(r => `${{escapeHtml(r.name)}} x${{r.quantity}}`).join(', ');

                // Render item name as a link to the source page
                const nameLink = `<a href="${{escapeHtml(item.url || '#')}}" target="_blank" rel="noopener">${{escapeHtml(item.name)}}</a>`;

                row.innerHTML = `
                    <td>${{nameLink}}</td>
                    <td>${{escapeHtml(item.category)}}</td>
                    <td>${{recyclingText || '—'}}</td>
                    <td>${{salvagingText || '—'}}</td>
                `;
                tableBody.appendChild(row);
            }});
        }}

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        // Sorting helpers
        function sortByName(items, asc=true) {{
            return items.sort((a,b) => {{
                const A = a.name.toLowerCase();
                const B = b.name.toLowerCase();
                if (A < B) return asc ? -1 : 1;
                if (A > B) return asc ? 1 : -1;
                return 0;
            }});
        }}

        function sortByRecycling(items, asc=true) {{
            return items.sort((a,b) => asc ? a.recyclingTotal - b.recyclingTotal : b.recyclingTotal - a.recyclingTotal);
        }}

        function sortBySalvaging(items, asc=true) {{
            return items.sort((a,b) => asc ? a.salvagingTotal - b.salvagingTotal : b.salvagingTotal - a.salvagingTotal);
        }}

        // Wire up buttons
        document.getElementById('sort-asc').addEventListener('click', () => {{
            const items = buildItems();
            const sorted = sortByName(items, true);
            renderTable(sorted);
        }});

        document.getElementById('sort-desc').addEventListener('click', () => {{
            const items = buildItems();
            const sorted = sortByName(items, false);
            renderTable(sorted);
        }});

        // Additional buttons for recycling and salvaging sort
        // Create them dynamically if not present
        const container = document.getElementById('sorting');
        if (container) {{
            const rAsc = document.createElement('button'); rAsc.textContent = 'Recycling ↑';
            const rDesc = document.createElement('button'); rDesc.textContent = 'Recycling ↓';
            const sAsc = document.createElement('button'); sAsc.textContent = 'Salvage ↑';
            const sDesc = document.createElement('button'); sDesc.textContent = 'Salvage ↓';

            container.appendChild(rAsc); container.appendChild(rDesc);
            container.appendChild(sAsc); container.appendChild(sDesc);

            rAsc.addEventListener('click', () => {{ renderTable(sortByRecycling(buildItems(), true)); }});
            rDesc.addEventListener('click', () => {{ renderTable(sortByRecycling(buildItems(), false)); }});
            sAsc.addEventListener('click', () => {{ renderTable(sortBySalvaging(buildItems(), true)); }});
            sDesc.addEventListener('click', () => {{ renderTable(sortBySalvaging(buildItems(), false)); }});
        }}

        // Initial render: sort by name ascending
        renderTable(sortByName(buildItems(), true));
    </script>'''

        return js


if __name__ == "__main__":
    pass
