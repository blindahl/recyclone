"""
Arc Raiders Recycling Tracker - Main Entry Point

Usage:
    python main.py                    # Generate HTML from existing JSON
    python main.py --scrape           # Scrape data and generate HTML
    python main.py --scrape --output custom.html --data custom.json
"""
import argparse
import sys
import os
import logging
from scraper import WikiScraper
from generator import HTMLGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Arc Raiders Recycling Tracker - Scrape and visualize item recycling data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py                    Generate HTML from existing JSON
  python main.py --scrape           Scrape data and generate HTML
  python main.py --output page.html Use custom output filename
        '''
    )
    
    parser.add_argument(
        '--scrape',
        action='store_true',
        help='Scrape data from wiki before generating HTML'
    )
    
    parser.add_argument(
        '--output',
        default='output/recycling_tracker.html',
        help='Output HTML file path (default: output/recycling_tracker.html)'
    )
    
    parser.add_argument(
        '--data',
        default='output/recycling_data.json',
        help='JSON data file path (default: output/recycling_data.json)'
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()
    
    logger.info("Arc Raiders Recycling Tracker")
    logger.info("=" * 50)
    
    try:
        # Step 1: Scrape data if requested
        if args.scrape:
            logger.info("Scraping data from Arc Raiders wiki...")
            scraper = WikiScraper()
            data = scraper.scrape_all_categories()
            scraper.save_to_json(data, args.data)
            logger.info(f"Data saved to {args.data}")
        else:
            # Check if JSON file exists
            if not os.path.exists(args.data):
                logger.error(f"Data file not found: {args.data}")
                logger.error("Please run with --scrape flag to generate the data file:")
                logger.error(f"  python main.py --scrape")
                sys.exit(1)
            logger.info(f"Using existing data file: {args.data}")
        
        # Step 2: Generate HTML
        logger.info("Generating HTML page...")
        generator = HTMLGenerator(args.data)
        generator.load_data()
        generator.generate_html(args.output)
        logger.info(f"HTML page generated: {args.output}")
        
        logger.info("=" * 50)
        logger.info("Success! Open the HTML file in your browser to view the tracker.")
        
    except KeyboardInterrupt:
        logger.info("\\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
