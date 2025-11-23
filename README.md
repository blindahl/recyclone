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
# Arc Raiders Recycling Tracker

A small Python tool that scrapes the Arc Raiders wiki (Loot page) and generates a standalone, sortable HTML report showing recycling and salvaging results for items.

This repository contains:

- `scraper.py` — scraping utilities (collects item links from the Loot page and extracts Recycling and Salvaging sections from each item page)
- `main.py` — CLI entrypoint. Orchestrates scraping and HTML generation
- `generator.py` — builds the static HTML file (embedded CSS/JS). Item names link back to the source wiki pages
- `requirements.txt` — Python dependencies
- `output/` — default output directory used by the CLI

## Highlights

- Scrapes the `https://arcraiders.wiki/wiki/Loot` page and individual item pages
- Produces `output/recycling_data.json` (data), `output/recycling_data.py` (Python module), and `output/recycling_tracker.html` (interactive page)
- The HTML shows separate columns for Recycling and Salvaging results and provides sorting by item name, recycling total, and salvaging total
- Item names are clickable links that open the original wiki page in a new tab

## Quick install (recommended)

Use a virtual environment to keep dependencies isolated:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

If you prefer not to use a venv, you can install globally or with `--user`:

```bash
python3 -m pip install --user -r requirements.txt
```

## Usage

Scrape the Loot page and generate outputs (JSON, Python module, HTML):

```bash
python main.py --scrape
```

Generate HTML from an existing JSON data file:

```bash
python main.py --data output/recycling_data.json --output output/recycling_tracker.html
```

Custom paths example:

```bash
python main.py --scrape --data custom_data.json --output custom_page.html
```

CLI options:

- `--scrape` — fetch fresh data from the wiki
- `--data <path>` — JSON data file path (default: `output/recycling_data.json`)
- `--output <path>` — HTML output path (default: `output/recycling_tracker.html`)

## Output files

- `output/recycling_data.json` — full scraped dataset
- `output/recycling_data.py` — Python module exposing `RECYCLING_DATA` (same data embedded as JSON)
- `output/recycling_tracker.html` — the generated static HTML report (open in a browser)

## How the scraper works (brief)

- The scraper loads the Loot page and parses the first table to find item links
- For each item page it looks for headings containing keywords like `Recycling` / `Salvaging` and parses tables, lists or inline text after that heading
- Materials are parsed using simple patterns (e.g. `Material: 5`, `Material (5)`, `5x Material`)
- Salvaging entries are preserved and marked during scraping so the generator can place them in their own column

## Notes & troubleshooting

- Scraping will make a sequence of HTTP requests; the scraper enforces a small rate-limit and uses retry-with-backoff for robustness. Expect scraping to take time for many items.
- If you hit network or permission issues when installing packages, use the venv approach described above or `--user` installs.
- If the wiki layout changes, the parsing functions (`_extract_from_table`, `_extract_from_list`, `_parse_material_text`, etc.) may need updates. Adding unit tests for parsing is recommended.

## Development

Run tests (if present):

```bash
python -m pytest tests/
```

Add a reproducible lockfile if desired:

```bash
pip freeze > requirements.lock
```

## Next improvements you might want

- Output structured `recycling` and `salvaging` lists per item in the JSON (instead of using a marker prefix)
- Add unit tests that assert parsing of representative HTML fragments
- Add a small CLI option to limit max items scraped for faster development

## License

No license file is included. If you want a specific open-source license added (MIT, Apache-2.0, etc.), tell me which one and I'll add it.

---

If you'd like the README adjusted (more examples, screenshots, or developer guidance), tell me what to include and I'll update it.
