# Implementation Plan

- [x] 1. Set up project structure and dependencies


  - Create project directory structure with main.py, scraper.py, generator.py
  - Create requirements.txt with requests, beautifulsoup4, lxml, hypothesis
  - Create tests directory with subdirectories for fixtures
  - _Requirements: 9.1, 9.2_



- [ ] 2. Implement core data models and JSON schema
  - [ ] 2.1 Define Material and Item dataclasses in scraper.py
    - Create Material dataclass with name and quantity fields
    - Create Item dataclass with name, category, url, and materials fields
    - Add type hints for all fields
    - _Requirements: 3.2, 3.3_
  
  - [ ]* 2.2 Write property test for JSON schema consistency
    - **Property 4: JSON schema consistency**
    - **Validates: Requirements 3.1**
  
  - [ ]* 2.3 Write property test for required item fields
    - **Property 5: Required item fields**
    - **Validates: Requirements 3.2**
  
  - [ ]* 2.4 Write property test for numeric quantity types
    - **Property 6: Numeric quantity types**


    - **Validates: Requirements 3.3**

- [ ] 3. Implement WikiScraper class with MediaWiki API integration
  - [x] 3.1 Create WikiScraper class with initialization and configuration


    - Implement __init__ with base_url and api_endpoint parameters
    - Set up requests session with connection pooling
    - Configure rate limiting (1 request per second)
    - _Requirements: 1.1, 2.1_
  
  - [ ] 3.2 Implement category page scraping
    - Write scrape_category method to fetch category pages
    - Extract item links from category pages using MediaWiki API or HTML parsing


    - Handle pagination if categories have many items
    - _Requirements: 1.2_
  
  - [ ]* 3.3 Write property test for link extraction completeness
    - **Property 2: Link extraction completeness**
    - **Validates: Requirements 1.2**
  
  - [ ] 3.4 Implement item page scraping and recycling data extraction
    - Write scrape_item_page method to fetch individual item pages


    - Implement extract_recycling_data to parse "Recycled & Salvaged Materials" section
    - Extract material names and quantities from HTML tables or lists
    - _Requirements: 1.3_
  
  - [ ]* 3.5 Write property test for material extraction accuracy
    - **Property 3: Material extraction accuracy**
    - **Validates: Requirements 1.3**



- [ ] 4. Implement error handling and retry logic for scraper
  - [ ] 4.1 Add retry logic with exponential backoff
    - Implement retry decorator or function with 3 attempts
    - Use delays of 1s, 2s, 4s between retries
    - Log each retry attempt
    - _Requirements: 7.1_
  
  - [ ]* 4.2 Write property test for retry behavior
    - **Property 12: Retry with exponential backoff**
    - **Validates: Requirements 7.1**


  
  - [ ] 4.3 Implement error handling for missing data and network failures
    - Handle missing "Recycled & Salvaged Materials" sections gracefully
    - Return empty materials list for items without recycling data
    - Log failed page retrievals with URLs and error messages
    - Continue processing after failures
    - _Requirements: 7.2, 2.3_
  


  - [ ]* 4.4 Write property test for error handling continuity
    - **Property 7: Error handling continuity**
    - **Validates: Requirements 2.3**

- [ ] 5. Implement complete scraping workflow
  - [ ] 5.1 Implement scrape_all_categories method
    - Define list of seven category URLs
    - Iterate through all categories and scrape each
    - Aggregate results into single data structure
    - _Requirements: 1.1_
  
  - [ ]* 5.2 Write property test for complete category coverage
    - **Property 1: Complete category coverage**
    - **Validates: Requirements 1.1**


  
  - [ ] 5.3 Implement JSON saving functionality
    - Write save_to_json method with atomic file writes
    - Include metadata (timestamp, item count, category count)
    - Handle file I/O errors with clear error messages


    - _Requirements: 1.4, 1.5_
  
  - [ ]* 5.4 Write unit tests for scraper module
    - Test HTML parsing with fixture files


    - Test URL construction
    - Test JSON serialization
    - _Requirements: 1.3, 1.4_

- [ ] 6. Checkpoint - Ensure scraper tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement HTMLGenerator class


  - [ ] 7.1 Create HTMLGenerator class with data loading
    - Implement __init__ with data_filepath parameter
    - Write load_data method to read and parse JSON file
    - Validate JSON structure against expected schema
    - Handle missing or invalid JSON files with clear errors


    - _Requirements: 4.1_
  
  - [ ] 7.2 Implement HTML structure generation
    - Write generate_html method to create complete HTML document
    - Generate DOCTYPE, html, head, and body structure

    - Embed CSS and JavaScript inline for standalone functionality
    - _Requirements: 4.3_
  
  - [ ] 7.3 Implement checkbox generation
    - Write generate_checkboxes_html to create checkbox elements for all items
    - Include item name and category in checkbox labels


    - Generate unique IDs for each checkbox
    - _Requirements: 5.1_
  
  - [ ]* 7.4 Write property test for HTML content completeness
    - **Property 8: HTML content completeness**

    - **Validates: Requirements 5.1**
  
  - [ ] 7.5 Implement materials table generation
    - Write generate_table_html to create initial table structure
    - Include table headers for material name and quantity
    - Generate table body with all materials from all items
    - _Requirements: 4.2_

- [x] 8. Implement CSS styling

  - [ ] 8.1 Write embed_css method with responsive checkbox layout
    - Use flexbox for horizontal checkbox layout with wrapping
    - Style checkboxes with appropriate spacing and sizing
    - Add responsive styles for mobile devices
    - Style table with borders, padding, and hover effects
    - _Requirements: 5.2_
  
  - [ ] 8.2 Add styling for controls and results sections
    - Style sort buttons with clear visual feedback
    - Add spacing between control sections
    - Ensure minimum touch target sizes (44x44px)
    - _Requirements: 6.1_

- [ ] 9. Implement JavaScript functionality
  - [ ] 9.1 Write checkbox filtering logic
    - Add event listeners to all checkboxes
    - Implement function to get selected items
    - Filter materials based on selected items
    - Update table display when selection changes
    - _Requirements: 5.3, 5.4_
  


  - [ ] 9.2 Implement material aggregation
    - Write function to aggregate materials from multiple selected items
    - Sum quantities for materials that appear in multiple items
    - Handle case when no items are selected (show all)


    - _Requirements: 5.5_
  
  - [ ]* 9.3 Write property test for material aggregation correctness
    - **Property 9: Material aggregation correctness**
    - **Validates: Requirements 5.5**
  
  - [ ] 9.4 Implement sorting functionality
    - Add event listeners to sort buttons
    - Write ascending sort function
    - Write descending sort function
    - Update table display after sorting
    - _Requirements: 6.2, 6.3_
  


  - [ ]* 9.5 Write property tests for sort correctness
    - **Property 10: Ascending sort correctness**
    - **Property 11: Descending sort correctness**
    - **Validates: Requirements 6.2, 6.3**
  
  - [ ]* 9.6 Write unit tests for generator module
    - Test JSON loading and validation
    - Test HTML generation with sample data
    - Test CSS and JavaScript embedding
    - _Requirements: 4.1, 4.2, 4.3_

- [ ] 10. Checkpoint - Ensure generator tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement main entry point script
  - [ ] 11.1 Create main.py with argument parsing
    - Use argparse to define --scrape, --output, and --data flags
    - Set default values for output and data file paths
    - Add help text for all arguments
    - _Requirements: 8.1, 8.2_
  
  - [ ] 11.2 Implement workflow orchestration logic
    - Check if --scrape flag is present
    - If --scrape: run scraper, then run generator
    - If not --scrape: check JSON exists, then run generator


    - Handle missing JSON file error with helpful message
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ]* 11.3 Write unit tests for main script
    - Test argument parsing


    - Test workflow with --scrape flag
    - Test workflow without --scrape flag
    - Test error handling for missing JSON
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 12. Implement backward compatibility
  - [ ] 12.1 Add version handling to JSON schema
    - Include schema version in metadata
    - Implement version checking in generator
    - Handle older schema versions gracefully
    - _Requirements: 9.3_
  
  - [ ]* 12.2 Write property test for backward compatibility
    - **Property 13: Backward compatibility**
    - **Validates: Requirements 9.3**

- [ ] 13. Create test fixtures and integration tests
  - [ ]* 13.1 Create HTML fixtures for testing
    - Create sample_category.html with known item links
    - Create sample_item.html with recycling materials section
    - Create sample_data.json with test data
    - _Requirements: 1.2, 1.3_
  
  - [ ]* 13.2 Write integration tests
    - Test end-to-end scraping with mocked HTTP responses
    - Test end-to-end generation from JSON to HTML
    - Test complete workflow from scrape to HTML generation
    - _Requirements: 1.1, 4.1_

- [ ] 14. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Create documentation
  - [ ] 15.1 Write README.md with usage instructions
    - Document installation steps
    - Provide usage examples for main.py
    - Explain command-line arguments
    - Include troubleshooting section
    - _Requirements: 8.1, 8.2_
  
  - [ ] 15.2 Add code documentation
    - Add docstrings to all classes and methods
    - Include type hints throughout codebase
    - Add inline comments for complex logic
    - _Requirements: 9.1, 9.2_
