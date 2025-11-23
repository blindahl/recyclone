# Arc Raiders Recycling Tracker

A Python tool to scrape item recycling data from the Arc Raiders wiki and generate an interactive HTML page for viewing and filtering recycling materials.

## Features

- 🔍 Scrapes recycling data from 7 item categories (Weapons, Augments, Shields, Healing, Quick Use, Grenades, Traps)
- 📊 Generates a standalone HTML page with embedded CSS and JavaScript
- ✅ Interactive checkboxes to filter items
- 🔄 Sort materials by quantity (ascending/descending)
- 📱 Responsive design that works on mobile and desktop
- 💾 Saves data to JSON for offline use

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### First Time: Scrape Data and Generate HTML

```bash
python main.py --scrape
```

This will:
1. Scrape all item recycling data from the Arc Raiders wiki
2. Save the data to `output/recycling_data.json`
3. Generate an interactive HTML page at `output/recycling_tracker.html`

### Generate HTML from Existing Data

If you already have the JSON data file:

```bash
python main.py
```

### Custom File Paths

```bash
python main.py --scrape --output custom_page.html --data custom_data.json
```

### Command-Line Options

- `--scrape`: Scrape data from the wiki before generating HTML
- `--output FILE`: Specify output HTML file path (default: `output/recycling_tracker.html`)
- `--data FILE`: Specify JSON data file path (default: `output/recycling_data.json`)

## Using the HTML Page

1. Open `output/recycling_tracker.html` in your web browser
2. Select items using the checkboxes at the top
3. The table will show aggregated recycling materials for selected items
4. Click "Sort Ascending ↑" or "Sort Descending ↓" to sort by quantity
5. If no items are selected, all materials from all items are shown

## Project Structure

```
arc-raiders-recycling-tracker/
├── main.py                    # Entry point script
├── scraper.py                 # Web scraping module
├── generator.py               # HTML generation module
├── requirements.txt           # Python dependencies
├── output/                    # Generated files (created on first run)
│   ├── recycling_data.json    # Scraped data
│   └── recycling_tracker.html # Interactive page
├── tests/                     # Test files
│   ├── test_scraper.py
│   ├── test_generator.py
│   ├── test_integration.py
│   └── fixtures/              # Test fixtures
└── README.md                  # This file
```

## How It Works

1. **Scraper Module** (`scraper.py`):
   - Fetches category pages from the Arc Raiders wiki
   - Extracts links to individual item pages
   - Parses the "Recycled & Salvaged Materials" section from each item page
   - Handles errors gracefully with retry logic
   - Saves structured data to JSON

2. **Generator Module** (`generator.py`):
   - Loads data from JSON file
   - Generates HTML with embedded CSS and JavaScript
   - Creates checkboxes for each item
   - Embeds interactive filtering and sorting logic

3. **Main Script** (`main.py`):
   - Parses command-line arguments
   - Orchestrates scraping and generation workflow
   - Provides helpful error messages

## Troubleshooting

### "Data file not found" Error

If you see this error, run the script with the `--scrape` flag:

```bash
python main.py --scrape
```

### Scraping Takes a Long Time

The scraper includes rate limiting (1 request per second) to avoid overwhelming the wiki server. This is intentional and respectful of the server resources.

### Network Errors

The scraper includes automatic retry logic with exponential backoff. If a page fails after 3 attempts, it will be logged and the scraper will continue with remaining pages.

## Requirements

- Python 3.7+
- requests
- beautifulsoup4

## License

MIT


## Development

### Running Tests

To run the test suite:

```bash
python -m pytest tests/
```

### Code Structure

The codebase follows a modular design:

- **Data Models**: `Material` and `Item` dataclasses in `scraper.py`
- **Scraping Logic**: `WikiScraper` class handles all web scraping with retry logic
- **HTML Generation**: `HTMLGenerator` class creates the interactive page
- **Main Orchestration**: `main.py` coordinates the workflow

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

- Data sourced from [Arc Raiders Wiki](https://arcraiders.wiki/)
- Built with Python, BeautifulSoup, and vanilla JavaScript
