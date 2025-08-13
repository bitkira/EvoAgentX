"""
Web Scraping Script Template

This template provides a basic structure for web scraping scripts.
Use this template to create scripts that extract data from websites.

Template Variables:
- target_url: URL to scrape
- output_file: Path to output file for scraped data
- scraping_description: Description of what data to scrape
- user_agent: User agent string for HTTP requests
"""

#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging
import time
import os
import sys
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WebScraper:
    """
    Web scraping class for {{scraping_description}}
    """
    
    def __init__(
        self, 
        target_url: str, 
        output_file: str,
        user_agent: str = None,
        delay: float = 1.0
    ):
        """
        Initialize the web scraper.
        
        Args:
            target_url: URL to scrape
            output_file: Path to output file
            user_agent: Custom user agent string
            delay: Delay between requests in seconds
        """
        self.target_url = target_url
        self.output_file = output_file
        self.delay = delay
        self.scraped_data = []
        
        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or '{{user_agent}}' or 'ALITA Web Scraper 1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        logger.info(f"WebScraper initialized: {target_url} -> {output_file}")
    
    def fetch_page(self, url: str, timeout: int = 30) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            logger.info(f"Fetching page: {url}")
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            logger.info(f"Page fetched successfully. Status code: {response.status_code}")
            
            # Add delay to be respectful to the server
            if self.delay > 0:
                time.sleep(self.delay)
            
            return soup
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching page {url}: {str(e)}")
            return None
    
    def extract_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract data from parsed HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of extracted data dictionaries
        """
        extracted_data = []
        
        try:
            logger.info("Extracting data from page...")
            
            # Customize this section based on the specific scraping requirements
            # Example: Extract all links
            links = soup.find_all('a', href=True)
            for link in links:
                data_item = {
                    'text': link.get_text(strip=True),
                    'url': urljoin(self.target_url, link['href']),
                    'title': link.get('title', ''),
                }
                extracted_data.append(data_item)
            
            # Example: Extract all paragraphs
            paragraphs = soup.find_all('p')
            for i, p in enumerate(paragraphs):
                data_item = {
                    'type': 'paragraph',
                    'index': i,
                    'text': p.get_text(strip=True),
                    'length': len(p.get_text(strip=True))
                }
                extracted_data.append(data_item)
            
            # Add more extraction logic here based on requirements
            # Example patterns:
            # - soup.find_all('div', class_='specific-class')
            # - soup.select('css-selector')
            # - soup.find_all('tag', attrs={'attribute': 'value'})
            
            logger.info(f"Extracted {len(extracted_data)} data items")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            return []
    
    def scrape_single_page(self) -> bool:
        """
        Scrape data from a single page.
        
        Returns:
            True if scraping successful, False otherwise
        """
        try:
            soup = self.fetch_page(self.target_url)
            if soup is None:
                return False
            
            extracted_data = self.extract_data(soup)
            if not extracted_data:
                logger.warning("No data extracted from page")
                return False
            
            self.scraped_data.extend(extracted_data)
            logger.info(f"Successfully scraped {len(extracted_data)} items")
            return True
            
        except Exception as e:
            logger.error(f"Error scraping single page: {str(e)}")
            return False
    
    def scrape_multiple_pages(self, urls: List[str]) -> int:
        """
        Scrape data from multiple pages.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            Number of successfully scraped pages
        """
        successful_scrapes = 0
        
        try:
            logger.info(f"Starting to scrape {len(urls)} pages...")
            
            for i, url in enumerate(urls, 1):
                logger.info(f"Processing page {i}/{len(urls)}: {url}")
                
                soup = self.fetch_page(url)
                if soup is None:
                    continue
                
                extracted_data = self.extract_data(soup)
                if extracted_data:
                    self.scraped_data.extend(extracted_data)
                    successful_scrapes += 1
                    logger.info(f"Page {i} scraped successfully")
                else:
                    logger.warning(f"No data extracted from page {i}")
            
            logger.info(f"Completed scraping. {successful_scrapes}/{len(urls)} pages successful")
            return successful_scrapes
            
        except Exception as e:
            logger.error(f"Error in multi-page scraping: {str(e)}")
            return successful_scrapes
    
    def save_data(self) -> bool:
        """
        Save scraped data to output file.
        
        Returns:
            True if data saved successfully, False otherwise
        """
        try:
            if not self.scraped_data:
                logger.error("No data to save")
                return False
            
            logger.info(f"Saving {len(self.scraped_data)} items to: {self.output_file}")
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
            # Detect output file type and save accordingly
            file_extension = os.path.splitext(self.output_file)[1].lower()
            
            if file_extension == '.json':
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
            elif file_extension == '.csv':
                df = pd.DataFrame(self.scraped_data)
                df.to_csv(self.output_file, index=False, encoding='utf-8')
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.DataFrame(self.scraped_data)
                df.to_excel(self.output_file, index=False)
            else:
                logger.warning(f"Unsupported output file type: {file_extension}")
                # Default to JSON
                with open(self.output_file + '.json', 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
            
            logger.info("Data saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of scraped data.
        
        Returns:
            Dictionary containing scraping summary
        """
        if not self.scraped_data:
            return {"error": "No data available"}
        
        try:
            summary = {
                "total_items": len(self.scraped_data),
                "target_url": self.target_url,
                "output_file": self.output_file,
                "data_types": {}
            }
            
            # Analyze data types
            if self.scraped_data:
                first_item = self.scraped_data[0]
                for key in first_item.keys():
                    summary["data_types"][key] = type(first_item[key]).__name__
            
            return summary
            
        except Exception as e:
            return {"error": f"Error generating summary: {str(e)}"}


def main():
    """
    Main function to execute web scraping workflow.
    """
    # Configuration
    target_url = "{{target_url}}"
    output_file = "{{output_file}}"
    
    # Validate input parameters
    if not target_url or target_url.startswith("{{"):
        logger.error("Target URL not specified or still contains placeholder")
        sys.exit(1)
    
    # Initialize scraper
    scraper = WebScraper(target_url, output_file)
    
    # Execute scraping workflow
    try:
        logger.info("Starting web scraping workflow...")
        logger.info(f"Target: {{scraping_description}}")
        
        # Scrape the target page
        if not scraper.scrape_single_page():
            logger.error("Failed to scrape target page")
            sys.exit(1)
        
        # Save scraped data
        if not scraper.save_data():
            logger.error("Failed to save scraped data")
            sys.exit(1)
        
        # Display summary
        summary = scraper.get_summary()
        logger.info("Scraping Summary:")
        for key, value in summary.items():
            logger.info(f"  {key}: {value}")
        
        print("✅ Web scraping completed successfully!")
        logger.info("Web scraping workflow completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in main workflow: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()