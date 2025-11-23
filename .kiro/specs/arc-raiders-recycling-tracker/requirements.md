# Requirements Document

## Introduction

This system scrapes item recycling data from the Arc Raiders wiki and generates an interactive HTML page for viewing and filtering recycling materials. The system consists of two main components: a data scraper that extracts and stores recycling information, and a static HTML generator that creates an interactive interface for exploring the data.

## Glossary

- **Scraper**: The Python script that extracts item and recycling data from the Arc Raiders wiki
- **Item**: A game object (weapon, augment, shield, healing item, quick use item, grenade, or trap) that can be recycled
- **Material**: A resource obtained when an item is recycled
- **Recycling Data**: The mapping of items to materials and quantities obtained from recycling
- **HTML Generator**: The Python script that creates a static HTML page from the scraped data
- **Interactive Page**: The generated HTML page that displays recycling data with filtering and sorting capabilities
- **MediaWiki API**: The API interface provided by MediaWiki sites for programmatic access to wiki content

## Requirements

### Requirement 1

**User Story:** As a user, I want to scrape recycling data from the Arc Raiders wiki, so that I can access the information without repeatedly querying the website.

#### Acceptance Criteria

1. WHEN the Scraper is executed, THE Scraper SHALL retrieve data from all seven item category pages (Weapons, Augments, Shields, Healing, Quick Use, Grenades, Traps)
2. WHEN the Scraper processes a category page, THE Scraper SHALL extract links to all individual item pages within that category
3. WHEN the Scraper processes an individual item page, THE Scraper SHALL extract the item name and all materials with quantities from the "Recycled & Salvaged Materials" section
4. WHEN the Scraper completes data extraction, THE Scraper SHALL save the structured data to a JSON file
5. WHEN the JSON file is created, THE JSON file SHALL contain all items organized by category with their associated recycling materials and quantities

### Requirement 2

**User Story:** As a user, I want the scraper to use the MediaWiki API when possible, so that data extraction is reliable and efficient.

#### Acceptance Criteria

1. WHEN the Scraper needs to retrieve page content, THE Scraper SHALL use the MediaWiki API endpoints where applicable
2. WHEN the MediaWiki API cannot provide required data, THE Scraper SHALL fall back to HTML parsing
3. WHEN the Scraper encounters API errors, THE Scraper SHALL handle errors gracefully and report which pages failed to process

### Requirement 3

**User Story:** As a user, I want the scraped data stored in a well-structured JSON format, so that it can be easily consumed by other scripts.

#### Acceptance Criteria

1. WHEN the Scraper saves data, THE JSON file SHALL use a consistent schema with item categories as top-level keys
2. WHEN an item is stored in the JSON file, THE item SHALL include the item name, category, and a list of materials with their quantities
3. WHEN material quantities are stored, THE quantities SHALL be represented as numeric values

### Requirement 4

**User Story:** As a user, I want to generate a static HTML page from the scraped data, so that I can view recycling information in a browser.

#### Acceptance Criteria

1. WHEN the HTML Generator is executed with a valid JSON file, THE HTML Generator SHALL create a static HTML file
2. WHEN the HTML page is opened in a browser, THE Interactive Page SHALL display all items and their recycling materials
3. WHEN the HTML page renders, THE Interactive Page SHALL include embedded CSS and JavaScript for standalone functionality

### Requirement 5

**User Story:** As a user, I want to filter items using checkboxes, so that I can focus on specific items of interest.

#### Acceptance Criteria

1. WHEN the Interactive Page loads, THE Interactive Page SHALL display checkboxes for all available items
2. WHEN checkboxes are displayed, THE checkboxes SHALL be arranged horizontally and wrap to multiple lines when the window width is insufficient
3. WHEN a user selects or deselects a checkbox, THE Interactive Page SHALL update the displayed data to show only selected items
4. WHEN no checkboxes are selected, THE Interactive Page SHALL display all items
5. WHEN a user selects multiple checkboxes, THE Interactive Page SHALL display the combined recycling data for all selected items

### Requirement 6

**User Story:** As a user, I want to sort materials by quantity, so that I can identify which materials are most or least abundant.

#### Acceptance Criteria

1. WHEN the Interactive Page displays material data, THE Interactive Page SHALL provide controls for sorting by quantity
2. WHEN a user activates ascending sort, THE Interactive Page SHALL display materials ordered from lowest to highest quantity
3. WHEN a user activates descending sort, THE Interactive Page SHALL display materials ordered from highest to lowest quantity
4. WHEN sorting is applied, THE sort order SHALL persist until the user changes it

### Requirement 7

**User Story:** As a user, I want the scraper to handle network errors and missing data, so that partial failures don't prevent data collection.

#### Acceptance Criteria

1. WHEN the Scraper encounters a network error, THE Scraper SHALL retry the request up to three times with exponential backoff
2. WHEN an item page lacks a "Recycled & Salvaged Materials" section, THE Scraper SHALL record the item with empty recycling data
3. WHEN the Scraper completes execution, THE Scraper SHALL report summary statistics including successful and failed page retrievals

### Requirement 8

**User Story:** As a user, I want a single entry point script with optional scraping, so that I can easily generate the HTML page with or without refreshing the data.

#### Acceptance Criteria

1. WHEN the main script is executed without arguments, THE main script SHALL generate the HTML page using the existing JSON file
2. WHEN the main script is executed with the --scrape flag, THE main script SHALL first execute the Scraper to refresh the JSON file and then generate the HTML page
3. WHEN the --scrape flag is used and no JSON file exists, THE main script SHALL create the JSON file through scraping
4. WHEN the main script is executed without the --scrape flag and no JSON file exists, THE main script SHALL report an error and instruct the user to run with --scrape

### Requirement 9

**User Story:** As a developer, I want clear separation between data collection and presentation, so that each component can be maintained independently.

#### Acceptance Criteria

1. WHEN the Scraper is modified, THE HTML Generator SHALL continue functioning without changes
2. WHEN the HTML Generator is modified, THE Scraper SHALL continue functioning without changes
3. WHEN the JSON schema is extended, THE changes SHALL be backward compatible with existing data files
