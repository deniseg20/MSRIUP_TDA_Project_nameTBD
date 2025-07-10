# web scraping Federally Qualified Health Centers (FQHC) data from HCAI website (CA)
import requests
from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FQHCScraper:
    def __init__(self, headless=True, timeout=15):
        self.base_url = "https://funding.hcai.ca.gov/fqhc-site-search/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.headless = headless
        self.timeout = timeout
    
    def scrape_with_requests(self):
        """
        Try scraping with requests/BeautifulSoup first (faster method)
        """
        try:
            logger.info("Attempting to scrape with requests...")
            session = requests.Session()
            session.headers.update(self.headers)
            
            response = session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for tables with various class names
            table_selectors = [
                'table.table',
                'table.dataTable',
                'table[id*="table"]',
                'table'
            ]
            
            table = None
            for selector in table_selectors:
                table = soup.select_one(selector)
                if table:
                    logger.info(f"Found table with selector: {selector}")
                    break
            
            if not table:
                logger.warning("No tables found with requests method.")
                return None
            
            return self.parse_table(table)
            
        except Exception as e:
            logger.error(f"Requests method failed: {str(e)}")
            return None
    
    def parse_table(self, table):
        """
        Parse HTML table and convert to structured data
        """
        if not table:
            return None
        
        data = []
        
        # Find headers
        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        else:
            # Try first row as headers
            first_row = table.find('tr')
            if first_row:
                # Check if first row contains th elements (likely headers)
                if first_row.find('th'):
                    headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
        
        logger.info(f"Found headers: {headers}")
        
        # Find data rows
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
        else:
            all_rows = table.find_all('tr')
            # Skip header row if we found headers
            start_index = 1 if headers else 0
            rows = all_rows[start_index:]
        
        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            
            if len(row_data) > 0 and any(cell.strip() for cell in row_data):
                # Create dictionary using headers as keys
                if headers and len(headers) == len(row_data):
                    row_dict = dict(zip(headers, row_data))
                else:
                    # Create generic column names if headers don't match
                    row_dict = {f"column_{i+1}": value for i, value in enumerate(row_data)}
                
                data.append(row_dict)
        
        logger.info(f"Parsed {len(data)} rows from table")
        return data
    
    def setup_selenium_driver(self):
        """
        Setup and return a configured Selenium WebDriver
        """
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"--user-agent={self.headers['User-Agent']}")
        
        # Additional options for stability
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def wait_for_table_load(self, driver):
        """
        Wait for table to load and return the table element
        """
        table_selectors = [
            (By.CSS_SELECTOR, "table.table"),
            (By.CSS_SELECTOR, "table.dataTable"),
            (By.CSS_SELECTOR, "table[id*='table']"),
            (By.TAG_NAME, "table")
        ]
        
        for by, selector in table_selectors:
            try:
                table = WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
                logger.info(f"Table found with selector: {selector}")
                return table
            except TimeoutException:
                continue
        
        raise TimeoutException("No table found within timeout period")
    
    def scrape_with_selenium(self):
        """
        Use Selenium for JavaScript-heavy sites with improved pagination handling
        """
        driver = None
        try:
            logger.info("Attempting to scrape with Selenium...")
            driver = self.setup_selenium_driver()
            
            driver.get(self.base_url)
            
            # Wait for page to load completely
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for table to load
            table = self.wait_for_table_load(driver)
            
            # Try to apply FQHC filter
            #self.try_apply_fqhc_filter(driver)
            
            # Wait a bit more for any dynamic content after filtering
            time.sleep(3)
            
            # Scrape all pages
            all_data = []
            seen = set()
            page_number = 1
            max_pages = 100
            consecutive_empty_pages = 0
            max_consecutive_empty = 3
            
            while page_number <= max_pages and consecutive_empty_pages < max_consecutive_empty:
                logger.info(f"Scraping page {page_number}...")
                
                # Get current page data
                try:
                    current_table = driver.find_element(By.TAG_NAME, "table")
                    table_html = current_table.get_attribute('outerHTML')
                    soup = BeautifulSoup(table_html, 'html.parser')
                    
                    page_data = self.parse_table(soup.find('table'))
                    
                    if page_data and len(page_data) > 0:
                        all_data.extend(page_data)
                        logger.info(f"Found {len(page_data)} records on page {page_number}")
                        consecutive_empty_pages = 0
                    else:
                        consecutive_empty_pages += 1
                        logger.warning(f"No data found on page {page_number} (empty page {consecutive_empty_pages})")
                    
                    # Try to go to next page
                    if not self.go_to_next_page(driver):
                        logger.info("No more pages available")
                        break
                    
                    page_number += 1
                    
                except Exception as e:
                    logger.error(f"Error scraping page {page_number}: {str(e)}")
                    consecutive_empty_pages += 1
                    if consecutive_empty_pages >= max_consecutive_empty:
                        break
                    
                    # Try to continue to next page even after error
                    if not self.go_to_next_page(driver):
                        break
                    page_number += 1
            
            logger.info(f"Total pages scraped: {page_number - 1}")
            logger.info(f"Total records collected: {len(all_data)}")
            
            return all_data
                
        except Exception as e:
            logger.error(f"Selenium method failed: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def go_to_next_page(self, driver):
        """
        Try to navigate to the next page, return True if successful
        """
        next_selectors = [
            "button[aria-label*='Next' i]",
            "button[title*='Next' i]",
            "a[aria-label*='Next' i]",
            "a[title*='Next' i]",
            ".pagination .next:not(.disabled)",
            ".pagination .page-next:not(.disabled)",
            ".dataTables_paginate .next:not(.disabled)",
            ".dataTables_paginate .paginate_button.next:not(.disabled)",
            ".page-link[aria-label*='Next' i]:not(.disabled)",
            "li.next:not(.disabled) a",
            "li.page-item.next:not(.disabled) a"
        ]
        
        # Try CSS selectors first
        for selector in next_selectors:
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, selector)
                if self.is_button_clickable(next_button):
                    self.click_next_button(driver, next_button)
                    return True
            except (NoSuchElementException, Exception):
                continue
        
        # Try XPath selectors for text-based matching
        xpath_selectors = [
            "//button[contains(translate(text(), 'NEXT', 'next'), 'next') and not(contains(@class, 'disabled'))]",
            "//a[contains(translate(text(), 'NEXT', 'next'), 'next') and not(contains(@class, 'disabled'))]",
            "//button[contains(text(), '>') and not(contains(@class, 'disabled'))]",
            "//a[contains(text(), '>') and not(contains(@class, 'disabled'))]"
        ]
        
        for xpath in xpath_selectors:
            try:
                next_button = driver.find_element(By.XPATH, xpath)
                if self.is_button_clickable(next_button):
                    self.click_next_button(driver, next_button)
                    return True
            except (NoSuchElementException, Exception):
                continue
        
        return False
    
    def is_button_clickable(self, button):
        """
        Check if a button is actually clickable
        """
        try:
            is_enabled = button.is_enabled()
            is_displayed = button.is_displayed()
            has_disabled_class = 'disabled' in button.get_attribute('class').lower()
            has_disabled_attr = button.get_attribute('disabled') is not None
            
            return is_enabled and is_displayed and not has_disabled_class and not has_disabled_attr
        except Exception:
            return False
    
    def click_next_button(self, driver, button):
        """
        Safely click the next button
        """
        try:
            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            
            # Try regular click first
            button.click()
            time.sleep(3)  # Wait for page to load
            
        except Exception as e:
            # Try JavaScript click as fallback
            try:
                driver.execute_script("arguments[0].click();", button)
                time.sleep(3)
            except Exception as js_error:
                raise Exception(f"Both regular and JS clicks failed: {str(e)}, {str(js_error)}")
    
    def filter_fqhc_data(self, all_data):
        """
        Filter the complete dataset for FQHC entries only
        """
        if not all_data:
            return []
        
        fqhc_data = []
        fqhc_keywords = [
            'federally qualified health centers (fqhc)',
            'federally qualified health center (fqhc)/comprehensive health center',
        ]
        
        exclude_keywords = [
            'look-a-like',
            'look a like',
            'lookalike'
        ]
        
        for record in all_data:
            # Convert all values to string and join for searching
            record_text = ' '.join(str(value) for value in record.values()).lower()
            
            # Check for FQHC indicators
            has_fqhc_keyword = any(keyword in record_text for keyword in fqhc_keywords)
            has_exclude_keyword = any(keyword in record_text for keyword in exclude_keywords)
            
            if has_fqhc_keyword and not has_exclude_keyword:
                fqhc_data.append(record)
        
        return fqhc_data
    
    def scrape_data(self):
        """
        Main method to scrape data, trying multiple approaches
        """
        logger.info("Starting FQHC data scraping...")
        
        # Try requests first (faster)
        data = self.scrape_with_requests()
        
        # If requests fails or returns no data, try Selenium
        if not data:
            logger.info("Requests method failed or returned no data, trying Selenium...")
            data = self.scrape_with_selenium()
        
        return data
    
    def save_to_json(self, data, filename="fqhc_data.json"):
        """
        Save data to JSON file with error handling
        """
        if data:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Data saved to {filename}")
                return True
            except Exception as e:
                logger.error(f"Error saving to JSON: {str(e)}")
                return False
        else:
            logger.warning("No data to save.")
            return False
    


def main():
    """
    Main execution function with improved error handling and reporting
    """
    # Initialize scraper (set headless=False to see browser in action)
    scraper = FQHCScraper(headless=True, timeout=20)
    
    try:
        # Scrape all the data first
        logger.info("Starting data scraping process...")
        all_data = scraper.scrape_data()
        
        if all_data:
            logger.info(f"Total records scraped from table: {len(all_data)}")
            
            # Show sample of all data for debugging
            if all_data:
                logger.info("Sample of first record:")
                logger.info(json.dumps(all_data[0], indent=2))
            
            # Filter for FQHC only
            #fqhc_data = scraper.filter_fqhc_data(all_data)
            
            # Save all data for reference
            scraper.save_to_json(all_data, "all_health_centers_data.json")
            
            '''if fqhc_data:
                # Save FQHC-specific data
                scraper.save_to_json(fqhc_data, "fqhc_data.json")
                
                logger.info(f"FQHC records found and saved: {len(fqhc_data)}")
                
                # Display FQHC data
                print("\n" + "="*60)
                print("FQHC RECORDS FOUND:")
                print("="*60)
                
                for i, record in enumerate(fqhc_data):
                    print(f"\nFQHC Record {i+1}:")
                    print(json.dumps(record, indent=2))
                    print("-" * 50)
                    
            else:
                logger.warning("No FQHC records found in the scraped data.")
                logger.info("Possible reasons:")
                logger.info("1. No FQHCs are listed on the site")
                logger.info("2. The filtering criteria need adjustment")
                logger.info("3. The data structure is different than expected")
                
                # Show some sample records to help debug
                if len(all_data) > 0:
                    logger.info("\nSample records for debugging:")
                    for i, record in enumerate(all_data):
                        logger.info(f"Sample record {i+1}: {record}")'''
                        
        else:
            logger.error("Failed to scrape any data.")
            logger.info("The website might:")
            logger.info("1. Require JavaScript/dynamic loading")
            logger.info("2. Have anti-bot protection")
            logger.info("3. Have changed its structure")
            logger.info("4. Require specific cookies or session data")
            logger.info("5. Be temporarily unavailable")
            
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()