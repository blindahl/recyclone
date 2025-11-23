# Design Document

## Overview

The Arc Raiders Recycling Tracker is a Python-based system that extracts item recycling data from the Arc Raiders wiki and generates an interactive HTML visualization. The system consists of three main Python modules: a scraper module that uses the MediaWiki API and HTML parsing to extract data, a generator module that creates a standalone HTML page with embedded JavaScript for interactivity, and a main entry point that orchestrates the workflow based on command-line arguments.

## Architecture

The system follows a pipeline architecture with three distinct stages:

1. **Data Collection Stage** (scraper.py): Fetches and parses wiki pages to extract recycling data
2. **Data Storage Stage**: Persists data in JSON format as an intermediate representation
3. **Presentation Stage** (generator.py): Transforms JSON data into an interactive HTML page

The main entry point (main.py) coordinates these stages based on user input via command-line flags.

### Component Diagram

```
┌─────────────┐
│   main.py   │
│  (CLI Entry)│
└──────┬──────┘
       │
       ├─────────────┐
       │             │
       ▼             ▼
┌─────────────┐  ┌──────────────┐
│ scraper.py  │  │generator.py  │
│             │  │              │
│ MediaWiki   │  │ HTML + CSS   │
│ API + HTML  │  │ + JavaScript │
│ Parsing     │  │              │
└──────┬──────┘  └──────┬───────┘
       │                │
       ▼                ▼
   ┌────────────────────────┐
   │   recycling_data.json  │
   └────────────────────────┘
```

## Components and Interfaces

### 1. Main Entry Point (main.py)

**Purpose**: Orchestrate the scraping and generation workflow based on command-line arguments.

**Interface**:
- Command-line arguments:
  - `--scrape`: Optional flag to trigger data scraping before HTML generation
  - `--output`: Optional path for the generated HTML file (default: "recycling_tracker.html")
  - `--data`: Optional path for the JSON data file (default: "recycling_data.json")

**Responsibilities**:
- Parse command-line arguments
- Check for existence of JSON data file
- Invoke scraper module when --scrape flag is present
- Invoke generator module to create HTML output
- Handle errors and provide user feedback

### 2. Scraper Module (scraper.py)

**Purpose**: Extract recycling data from the Arc Raiders wiki using the MediaWiki API and HTML parsing.

**Key Classes**:

```python
class WikiScraper:
    def __init__(self, base_url: str, api_endpoint: str)
    def scrape_all_categories(self) -> dict
    def scrape_category(self, category_url: str) -> list[dict]
    def scrape_item_page(self, item_url: str) -> dict
    def extract_recycling_data(self, html_content: str) -> list[dict]
    def save_to_json(self, data: dict, filepath: str) -> None
```

**Data Flow**:
1. Fetch category pages (Weapons, Augments, etc.)
2. Extract item page links from each category
3. For each item, fetch the page and parse the "Recycled & Salvaged Materials" section
4. Structure data and save to JSON

**API Strategy**:
- Use MediaWiki API `action=parse` to get rendered HTML content
- Use MediaWiki API `action=query` with `prop=links` to discover item pages
- Fall back to direct HTTP requests with BeautifulSoup for HTML parsing when API is insufficient

**Error Handling**:
- Retry failed requests up to 3 times with exponential backoff (1s, 2s, 4s)
- Log failed pages to a separate error log
- Continue processing remaining items even if some fail

### 3. Generator Module (generator.py)

**Purpose**: Transform JSON data into a standalone interactive HTML page.

**Key Classes**:

```python
class HTMLGenerator:
    def __init__(self, data_filepath: str)
    def load_data(self) -> dict
    def generate_html(self, output_filepath: str) -> None
    def generate_checkboxes_html(self, items: list) -> str
    def generate_table_html(self) -> str
    def embed_css(self) -> str
    def embed_javascript(self) -> str
```

**HTML Structure**:
```html
<!DOCTYPE html>
<html>
<head>
    <style>/* Embedded CSS */</style>
</head>
<body>
    <div id="controls">
        <div id="checkboxes"><!-- Item checkboxes --></div>
        <div id="sorting">
            <button id="sort-asc">Sort Ascending</button>
            <button id="sort-desc">Sort Descending</button>
        </div>
    </div>
    <div id="results">
        <table id="materials-table"><!-- Material data --></table>
    </div>
    <script>/* Embedded JavaScript */</script>
</body>
</html>
```

**JavaScript Functionality**:
- Filter materials based on selected item checkboxes
- Aggregate material quantities when multiple items are selected
- Sort materials by quantity (ascending/descending)
- Update table dynamically without page reload

## Data Models

### JSON Schema

```json
{
  "categories": {
    "Weapons": [
      {
        "name": "Item Name",
        "url": "https://arcraiders.wiki/wiki/Item_Name",
        "materials": [
          {
            "material": "Material Name",
            "quantity": 10
          }
        ]
      }
    ],
    "Augments": [...],
    "Shields": [...],
    "Healing": [...],
    "Quick Use": [...],
    "Grenades": [...],
    "Traps": [...]
  },
  "metadata": {
    "scraped_at": "2025-11-23T12:00:00Z",
    "total_items": 150,
    "categories_count": 7
  }
}
```

### Internal Data Structures

**Item Model**:
```python
@dataclass
class Material:
    name: str
    quantity: int

@dataclass
class Item:
    name: str
    category: str
    url: str
    materials: list[Material]
```

## Corre
ctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Complete category coverage
*For any* execution of the scraper, the resulting JSON file should contain exactly seven category keys: "Weapons", "Augments", "Shields", "Healing", "Quick Use", "Grenades", and "Traps"
**Validates: Requirements 1.1**

### Property 2: Link extraction completeness
*For any* category page HTML with N item links, the scraper should extract all N links without duplication
**Validates: Requirements 1.2**

### Property 3: Material extraction accuracy
*For any* item page HTML containing a "Recycled & Salvaged Materials" section with M materials, the scraper should extract all M materials with their correct quantities
**Validates: Requirements 1.3**

### Property 4: JSON schema consistency
*For any* generated JSON file, the structure should conform to the defined schema with categories as top-level keys and items as arrays
**Validates: Requirements 3.1**

### Property 5: Required item fields
*For any* item in the JSON file, it should contain the fields "name", "url", and "materials"
**Validates: Requirements 3.2**

### Property 6: Numeric quantity types
*For any* material quantity in the JSON file, the value should be a numeric type (integer or float), not a string
**Validates: Requirements 3.3**

### Property 7: Error handling continuity
*For any* sequence of page requests where some fail, the scraper should continue processing remaining pages and log all failures
**Validates: Requirements 2.3**

### Property 8: HTML content completeness
*For any* valid JSON file with N items, the generated HTML should contain N checkbox elements corresponding to those items
**Validates: Requirements 5.1**

### Property 9: Material aggregation correctness
*For any* subset of selected items, the aggregated material quantities should equal the sum of quantities from each selected item's materials
**Validates: Requirements 5.5**

### Property 10: Ascending sort correctness
*For any* list of materials with quantities, applying ascending sort should result in a list where each element's quantity is less than or equal to the next element's quantity
**Validates: Requirements 6.2**

### Property 11: Descending sort correctness
*For any* list of materials with quantities, applying descending sort should result in a list where each element's quantity is greater than or equal to the next element's quantity
**Validates: Requirements 6.3**

### Property 12: Retry with exponential backoff
*For any* network request that fails, the scraper should retry up to 3 times with delays of 1s, 2s, and 4s between attempts
**Validates: Requirements 7.1**

### Property 13: Backward compatibility
*For any* JSON file generated by an older version of the scraper, the current HTML generator should successfully parse and render it
**Validates: Requirements 9.3**

## Error Handling

### Scraper Error Handling

1. **Network Errors**:
   - Implement retry logic with exponential backoff (1s, 2s, 4s)
   - Log failed requests with URL and error message
   - Continue processing remaining items after max retries exceeded

2. **Parsing Errors**:
   - Catch HTML parsing exceptions and log the problematic page
   - Return empty materials list for items with missing or malformed recycling sections
   - Validate extracted data before adding to results

3. **API Errors**:
   - Handle HTTP error codes (404, 500, etc.) gracefully
   - Fall back to direct HTML parsing if API requests fail
   - Log API-specific errors separately for debugging

4. **File I/O Errors**:
   - Check write permissions before saving JSON
   - Use atomic writes (write to temp file, then rename) to prevent corruption
   - Provide clear error messages if JSON cannot be saved

### Generator Error Handling

1. **Missing JSON File**:
   - Check file existence before attempting to load
   - Provide clear error message directing user to run with --scrape flag

2. **Invalid JSON**:
   - Validate JSON structure against expected schema
   - Report specific schema violations to help debugging
   - Fail fast with descriptive error rather than generating broken HTML

3. **Empty Data**:
   - Handle edge case of JSON with no items gracefully
   - Generate valid HTML with appropriate "no data" message

### Main Script Error Handling

1. **Command-line Argument Errors**:
   - Validate all provided file paths
   - Provide usage help if invalid arguments supplied

2. **Module Import Errors**:
   - Check for required dependencies (requests, beautifulsoup4)
   - Provide installation instructions if dependencies missing

## Testing Strategy

### Unit Testing

The system will use Python's built-in `unittest` framework for unit tests. Unit tests will focus on:

1. **Scraper Module**:
   - Parsing HTML snippets with known structure
   - Handling missing recycling sections
   - URL construction and validation
   - JSON serialization

2. **Generator Module**:
   - Loading and validating JSON data
   - HTML template generation
   - CSS and JavaScript embedding

3. **Main Script**:
   - Command-line argument parsing
   - File existence checks
   - Module orchestration logic

### Property-Based Testing

The system will use the `hypothesis` library for property-based testing. Property-based tests will verify:

1. **Data Integrity Properties**:
   - JSON schema consistency across all generated files
   - Material quantity aggregation correctness
   - Sort order correctness for any input data

2. **Robustness Properties**:
   - Scraper handles any valid HTML structure
   - Generator produces valid HTML for any valid JSON input
   - Retry logic executes correct number of times with proper delays

3. **Completeness Properties**:
   - All categories are always present in output
   - All items from input appear in output
   - No data loss during transformation pipeline

**Configuration**:
- Each property-based test will run a minimum of 100 iterations
- Tests will use custom generators for Item, Material, and JSON data structures
- Each property test will include a comment tag referencing the design document property

**Test Tagging Format**:
```python
# Feature: arc-raiders-recycling-tracker, Property 1: Complete category coverage
@given(...)
def test_category_coverage(data):
    ...
```

### Integration Testing

Integration tests will verify the end-to-end workflow:

1. Run scraper with mocked HTTP responses
2. Verify JSON file is created with expected structure
3. Run generator with the created JSON
4. Verify HTML file is created and contains expected elements

### Manual Testing

Manual testing will cover:

1. Visual verification of HTML page layout
2. Interactive testing of checkbox filtering
3. Testing of sort functionality in browser
4. Responsive design verification at different window sizes

## Implementation Notes

### Dependencies

**Required Python Packages**:
- `requests`: HTTP library for API calls and web scraping
- `beautifulsoup4`: HTML parsing library
- `lxml`: Fast XML/HTML parser for BeautifulSoup
- `hypothesis`: Property-based testing framework

**Development Dependencies**:
- `pytest`: Test runner
- `pytest-cov`: Code coverage reporting
- `black`: Code formatter
- `mypy`: Static type checker

### MediaWiki API Usage

The Arc Raiders wiki uses MediaWiki, which provides several useful API endpoints:

1. **Get page content**: `api.php?action=parse&page=PageName&format=json`
2. **Get page links**: `api.php?action=query&titles=PageName&prop=links&format=json`
3. **Get category members**: `api.php?action=query&list=categorymembers&cmtitle=Category:Name&format=json`

The scraper will use these endpoints where possible, falling back to HTML parsing when necessary.

### HTML/CSS/JavaScript Design

**CSS Framework**: None (vanilla CSS for simplicity and zero dependencies)

**JavaScript**: Vanilla JavaScript (no frameworks) for:
- Checkbox event handling
- Material aggregation logic
- Dynamic table updates
- Sort functionality

**Responsive Design**:
- Flexbox for checkbox layout with wrapping
- CSS media queries for mobile-friendly display
- Minimum touch target size of 44x44px for checkboxes

### Performance Considerations

1. **Scraping Performance**:
   - Implement rate limiting (1 request per second) to avoid overwhelming the wiki
   - Use connection pooling for HTTP requests
   - Cache category page results during a single scrape session

2. **HTML Generation Performance**:
   - Use string builder pattern for large HTML generation
   - Pre-calculate aggregated data structures
   - Minimize JavaScript execution on page load

3. **Browser Performance**:
   - Limit DOM updates during filtering/sorting
   - Use document fragments for batch DOM updates
   - Debounce checkbox change events if needed

### File Structure

```
arc-raiders-recycling-tracker/
├── main.py                 # Entry point script
├── scraper.py             # Scraping module
├── generator.py           # HTML generation module
├── recycling_data.json    # Generated data file
├── recycling_tracker.html # Generated HTML page
├── requirements.txt       # Python dependencies
├── tests/
│   ├── test_scraper.py
│   ├── test_generator.py
│   ├── test_integration.py
│   └── fixtures/
│       ├── sample_category.html
│       ├── sample_item.html
│       └── sample_data.json
└── README.md              # Usage instructions
```

## Future Enhancements

Potential improvements for future versions:

1. **Caching**: Implement HTTP caching to avoid re-scraping unchanged pages
2. **Incremental Updates**: Support updating only changed items rather than full re-scrape
3. **Search Functionality**: Add text search to filter items by name
4. **Material Filtering**: Add checkboxes to filter by specific materials
5. **Export Options**: Support exporting filtered data to CSV or JSON
6. **Dark Mode**: Add theme toggle for dark/light mode
7. **Comparison Mode**: Allow comparing recycling efficiency across items
8. **Mobile App**: Create a mobile-friendly PWA version
