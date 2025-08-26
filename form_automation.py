#!/usr/bin/env python3
"""
Form Automation Script
Automates filling and submitting application forms on web pages.
"""

import time
import json
import logging
import argparse
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
from random_values_generator import generate_test_data_for_state, RandomValuesGenerator

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FormAutomation:
    def __init__(self, headless: bool = False, timeout: int = 5):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        # Create a persistent random values generator instance
        self.random_generator = RandomValuesGenerator()
        self.generated_data = {}
        
    def get_generated_value(self, field_name):
        """Get a specific generated value by field name with logging"""
        if field_name in self.generated_data:
            value = self.generated_data[field_name]
            logger.info(f"Retrieved generated value for '{field_name}': {value}")
            return value
        else:
            logger.warning(f"Generated value for '{field_name}' not found")
            return None
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with options"""
        chrome_options = webdriver.ChromeOptions()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Get ChromeDriver path and fix the path issue
        driver_path = ChromeDriverManager().install()
        # Fix the path if it points to the wrong file
        if driver_path.endswith('THIRD_PARTY_NOTICES.chromedriver'):
            driver_path = driver_path.replace('THIRD_PARTY_NOTICES.chromedriver', 'chromedriver')
        
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, self.timeout)
        
        logger.info("WebDriver initialized successfully")
        
    def substitute_generated_values(self, config: Dict, generated_data: Dict):
        """Substitute generated test data values in configuration"""
        if not generated_data:
            logger.warning("No generated data available for substitution")
            return config
            
        # Create a copy of the config to avoid modifying the original
        import copy
        updated_config = copy.deepcopy(config)
        
        logger.info("=== STARTING VALUE SUBSTITUTION ===")
        substitution_map = {
            '{{zipCode}}': 'zipCode',
            '{{firstName}}': 'firstName', 
            '{{lastName}}': 'lastName',
            '{{ssn}}': 'ssn',
            '{{address}}': 'address',
            '{{dateOfBirth}}': 'dateOfBirth',
            '{{mbi}}': 'ssn'  # Use SSN for MBI if needed
        }
        
        # Substitute values in pages
        if 'pages' in updated_config:
            for page_idx, page in enumerate(updated_config['pages']):
                page_name = page.get('name', f'Page {page_idx + 1}')
                logger.info(f"Processing substitutions for {page_name}")
                if 'fields' in page:
                    for field in page['fields']:
                        field_value = field.get('value')
                        if field_value in substitution_map:
                            data_key = substitution_map[field_value]
                            if data_key in generated_data:
                                field['value'] = generated_data[data_key]
                                logger.info(f"  Substituted {field_value} -> {generated_data[data_key]} (field: {field.get('selector', 'unknown')})")
                            else:
                                logger.warning(f"  Data key '{data_key}' not found in generated data")
        
        # Substitute values in legacy single page fields
        if 'fields' in updated_config:
            logger.info("Processing substitutions for single page fields")
            for field in updated_config['fields']:
                field_value = field.get('value')
                if field_value in substitution_map:
                    data_key = substitution_map[field_value]
                    if data_key in generated_data:
                        field['value'] = generated_data[data_key]
                        logger.info(f"  Substituted {field_value} -> {generated_data[data_key]} (field: {field.get('selector', 'unknown')})")
                    else:
                        logger.warning(f"  Data key '{data_key}' not found in generated data")
        
        logger.info("=== VALUE SUBSTITUTION COMPLETE ===")
        return updated_config
        
    def dismiss_cookie_banner(self, banner_config: Optional[Dict] = None):
        """Dismiss cookie banner if present"""
        try:
            # Default cookie banner selectors to try
            default_selectors = [
                {"selector_type": "xpath", "selector": "//button[@aria-label='Close']"},
                {"selector_type": "xpath", "selector": "//button[contains(@aria-label, 'close')]"},
                {"selector_type": "xpath", "selector": "//button[contains(@class, 'cookie') and contains(@class, 'close')]"},
                {"selector_type": "xpath", "selector": "//button[contains(@id, 'cookie') and contains(@id, 'close')]"},
                {"selector_type": "xpath", "selector": "//button[contains(text(), 'Accept')]"},
                {"selector_type": "xpath", "selector": "//button[contains(text(), 'OK')]"},
                {"selector_type": "xpath", "selector": "//button[contains(text(), 'Got it')]"},
                {"selector_type": "css_selector", "selector": "[data-testid*='cookie'] button"},
                {"selector_type": "css_selector", "selector": ".cookie-banner button"},
                {"selector_type": "css_selector", "selector": "#cookie-banner button"}
            ]
            
            selectors_to_try = []
            
            # Use custom banner config if provided
            if banner_config:
                selectors_to_try.append({
                    "selector_type": banner_config.get("selector_type", "xpath"),
                    "selector": banner_config.get("selector")
                })
            
            # Add default selectors
            selectors_to_try.extend(default_selectors)
            
            for selector_config in selectors_to_try:
                try:
                    selector_type = selector_config["selector_type"]
                    selector = selector_config["selector"]
                    
                    if not selector:
                        continue
                        
                    by_type = getattr(By, selector_type.upper())
                    
                    # Try to find the element with a short timeout
                    element = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((by_type, selector))
                    )
                    
                    element.click()
                    logger.info(f"Successfully dismissed cookie banner using selector: {selector}")
                    time.sleep(1)  # Wait for banner to disappear
                    return True
                    
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.debug(f"Failed to dismiss banner with selector {selector}: {str(e)}")
                    continue
            
            logger.debug("No cookie banner found or banner already dismissed")
            return False
            
        except Exception as e:
            logger.error(f"Error while trying to dismiss cookie banner: {str(e)}")
            return False

    def load_page(self, url: str, dismiss_banner: bool = True, banner_config: Optional[Dict] = None):
        """Load the target web page and optionally dismiss cookie banner"""
        try:
            self.driver.get(url)
            logger.info(f"Successfully loaded page: {url}")
            time.sleep(2)
            
            # Try to dismiss cookie banner if requested
            if dismiss_banner:
                self.dismiss_cookie_banner(banner_config)
                
        except Exception as e:
            logger.error(f"Failed to load page {url}: {str(e)}")
            raise
            
    def fill_text_field(self, selector: str, value: str, selector_type: str = "id"):
        """Fill a text field with the given value"""
        import time
        start_time = time.time()
        try:
            by_type = getattr(By, selector_type.upper())
            logger.info(f"Looking for field: {selector} (type: {selector_type})")
            # Wait for element to be both present and interactable
            element = self.wait.until(EC.element_to_be_clickable((by_type, selector)))
            find_time = time.time()
            logger.info(f"Found field {selector} in {find_time - start_time:.2f} seconds")
            
            element.clear()
            element.send_keys(value)
            total_time = time.time() - start_time
            logger.info(f"Filled field {selector} with value: {value} (total time: {total_time:.2f}s)")
            return True
        except TimeoutException:
            total_time = time.time() - start_time
            logger.error(f"Field {selector} not found or not interactable within {self.timeout} seconds (waited {total_time:.2f}s)")
            return False
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Error filling field {selector}: {str(e)} (time: {total_time:.2f}s)")
            return False
            
    def select_dropdown(self, selector: str, value: str, selector_type: str = "id"):
        """Select an option from a dropdown"""
        try:
            by_type = getattr(By, selector_type.upper())
            element = self.wait.until(EC.presence_of_element_located((by_type, selector)))
            select = Select(element)
            select.select_by_visible_text(value)
            logger.info(f"Selected '{value}' from dropdown {selector}")
            return True
        except TimeoutException:
            logger.error(f"Dropdown {selector} not found")
            return False
        except Exception as e:
            logger.error(f"Error selecting from dropdown {selector}: {str(e)}")
            return False
            
    def click_element(self, selector: str, selector_type: str = "id"):
        """Click an element (button, checkbox, etc.)"""
        try:
            by_type = getattr(By, selector_type.upper())
            element = self.wait.until(EC.element_to_be_clickable((by_type, selector)))
            element.click()
            logger.info(f"Clicked element: {selector}")
            return True
        except TimeoutException:
            logger.error(f"Element {selector} not found or not clickable")
            return False
        except Exception as e:
            logger.error(f"Error clicking element {selector}: {str(e)}")
            return False
            
    def upload_file(self, selector: str, file_path: str, selector_type: str = "id"):
        """Upload a file to a file input element"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
                
            by_type = getattr(By, selector_type.upper())
            element = self.wait.until(EC.presence_of_element_located((by_type, selector)))
            element.send_keys(file_path)
            logger.info(f"Uploaded file {file_path} to {selector}")
            return True
        except TimeoutException:
            logger.error(f"File input {selector} not found")
            return False
        except Exception as e:
            logger.error(f"Error uploading file to {selector}: {str(e)}")
            return False
            
    def wait_for_element(self, selector: str, selector_type: str = "id", timeout: Optional[int] = None):
        """Wait for an element to be present"""
        wait_time = timeout or self.timeout
        try:
            by_type = getattr(By, selector_type.upper())
            wait = WebDriverWait(self.driver, wait_time)
            element = wait.until(EC.presence_of_element_located((by_type, selector)))
            return element
        except TimeoutException:
            logger.error(f"Element {selector} not found within {wait_time} seconds")
            return None
            
    def submit_form(self, submit_selector: str = None, selector_type: str = "id"):
        """Submit the form"""
        try:
            if submit_selector:
                return self.click_element(submit_selector, selector_type)
            else:
                # Try to find and click submit button
                submit_buttons = ["submit", "Submit", "SUBMIT", "send", "Send"]
                for button_text in submit_buttons:
                    try:
                        element = self.driver.find_element(By.XPATH, f"//input[@type='submit' and @value='{button_text}']")
                        element.click()
                        logger.info(f"Submitted form using submit button with value: {button_text}")
                        return True
                    except NoSuchElementException:
                        continue
                        
                # Try button tags
                for button_text in submit_buttons:
                    try:
                        element = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{button_text}')]")
                        element.click()
                        logger.info(f"Submitted form using button with text: {button_text}")
                        return True
                    except NoSuchElementException:
                        continue
                        
                logger.error("No submit button found")
                return False
        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            return False
            
    def fill_page_fields(self, fields: List[Dict]):
        """Fill fields on a single page"""
        success_count = 0
        total_fields = len(fields)
        
        for field in fields:
            field_type = field.get('type', 'text')
            selector = field.get('selector')
            selector_type = field.get('selector_type', 'id')
            value = field.get('value')
            
            if field_type == 'text':
                if self.fill_text_field(selector, value, selector_type):
                    success_count += 1
            elif field_type == 'dropdown':
                if self.select_dropdown(selector, value, selector_type):
                    success_count += 1
            elif field_type == 'click':
                if self.click_element(selector, selector_type):
                    success_count += 1
            elif field_type == 'file':
                if self.upload_file(selector, value, selector_type):
                    success_count += 1
                    
            time.sleep(0.2)  # Reduced delay between actions
            
        logger.info(f"Successfully filled {success_count}/{total_fields} fields on current page")
        return success_count == total_fields
    
    def navigate_to_next_page(self, navigation_config: Dict):
        """Navigate to the next page based on configuration"""
        nav_type = navigation_config.get('type', 'submit')
        
        if nav_type == 'submit':
            selector = navigation_config.get('selector')
            selector_type = navigation_config.get('selector_type', 'id')
            
            if self.submit_form(selector, selector_type):
                logger.info("Successfully navigated to next page via submit")
                
                # Wait for next page to load
                wait_time = navigation_config.get('wait_time', 3)
                time.sleep(wait_time)
                
                # Wait for specific element if configured
                if navigation_config.get('wait_for_element'):
                    wait_element = navigation_config['wait_for_element']
                    wait_selector = wait_element.get('selector')
                    wait_selector_type = wait_element.get('selector_type', 'id')
                    wait_timeout = wait_element.get('timeout', 30)
                    
                    if self.wait_for_element(wait_selector, wait_selector_type, wait_timeout):
                        logger.info("Next page loaded successfully")
                        return True
                    else:
                        logger.error("Failed to detect next page load")
                        return False
                return True
            else:
                logger.error("Failed to navigate to next page")
                return False
        elif nav_type == 'click':
            selector = navigation_config.get('selector')
            selector_type = navigation_config.get('selector_type', 'id')
            
            if self.click_element(selector, selector_type):
                logger.info("Successfully navigated to next page via click")
                
                wait_time = navigation_config.get('wait_time', 3)
                time.sleep(wait_time)
                return True
            else:
                logger.error("Failed to click navigation element")
                return False
        elif nav_type == 'url':
            url = navigation_config.get('url')
            if url:
                self.load_page(url)
                return True
            else:
                logger.error("No URL provided for navigation")
                return False
        else:
            logger.error(f"Unknown navigation type: {nav_type}")
            return False
    
    def fill_multipage_form(self, config: Dict):
        """Fill a multi-page form based on configuration"""
        pages = config.get('pages', [])
        
        if not pages:
            logger.warning("No pages configured, falling back to single page mode")
            return self.fill_page_fields(config.get('fields', []))
        
        total_success = True
        
        for page_index, page_config in enumerate(pages):
            page_name = page_config.get('name', f'Page {page_index + 1}')
            logger.info(f"Processing {page_name}")
            
            # Dismiss cookie banner if configured for this page
            if page_config.get('dismiss_cookie_banner', page_index == 0):  # Default to first page only
                banner_config = page_config.get('cookie_banner_config')
                self.dismiss_cookie_banner(banner_config)
            
            # Wait for page to be ready if configured
            if page_config.get('wait_for_page_ready'):
                page_ready_config = page_config['wait_for_page_ready']
                ready_selector = page_ready_config.get('selector')
                ready_selector_type = page_ready_config.get('selector_type', 'id')
                ready_timeout = page_ready_config.get('timeout', 30)
                
                if not self.wait_for_element(ready_selector, ready_selector_type, ready_timeout):
                    logger.error(f"Page {page_name} failed to load properly")
                    total_success = False
                    break
            
            # Fill fields on current page
            fields = page_config.get('fields', [])
            if fields:
                page_success = self.fill_page_fields(fields)
                if not page_success:
                    logger.error(f"Failed to fill all fields on {page_name}")
                    total_success = False
                    # Continue to next page anyway if configured
                    if not page_config.get('continue_on_error', False):
                        break
            
            # Navigate to next page if not the last page
            if page_index < len(pages) - 1:
                navigation = page_config.get('navigation')
                if navigation:
                    if not self.navigate_to_next_page(navigation):
                        logger.error(f"Failed to navigate from {page_name}")
                        total_success = False
                        break
                else:
                    logger.warning(f"No navigation configured for {page_name}")
            
            # Take screenshot of current page if configured
            if page_config.get('take_screenshot', False):
                screenshot_name = page_config.get('screenshot_name', f'{page_name.lower().replace(" ", "_")}.png')
                self.take_screenshot(screenshot_name)
        
        logger.info(f"Multi-page form processing {'completed successfully' if total_success else 'completed with errors'}")
        return total_success
        
    def fill_form_from_config(self, config: Dict):
        """Fill form based on configuration - supports both single and multi-page"""
        if config.get('pages'):
            return self.fill_multipage_form(config)
        else:
            # Legacy single page support
            success_count = 0
            total_fields = len(config.get('fields', []))
            
            success = self.fill_page_fields(config.get('fields', []))
            
            # Submit form if configured
            if config.get('submit'):
                submit_config = config['submit']
                submit_selector = submit_config.get('selector')
                submit_selector_type = submit_config.get('selector_type', 'id')
                
                if self.submit_form(submit_selector, submit_selector_type):
                    logger.info("Form submitted successfully")
                    
                    # Wait for confirmation or next page
                    if submit_config.get('wait_for_confirmation'):
                        confirmation_selector = submit_config.get('confirmation_selector')
                        confirmation_selector_type = submit_config.get('confirmation_selector_type', 'id')
                        
                        if self.wait_for_element(confirmation_selector, confirmation_selector_type, 30):
                            logger.info("Form submission confirmed")
                        else:
                            logger.warning("Form submission confirmation not detected")
                            
            return success
        
    def take_screenshot(self, filename: str = "screenshot.png"):
        """Take a screenshot of the current page"""
        try:
            if self.driver is None:
                logger.error("Cannot take screenshot: WebDriver not initialized")
                return False
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved as {filename}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return False
            
    def close(self):
        """Close the browser and clean up"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


def main():
    """Main function to run the form automation"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Form Automation with Test Data Generation')
    parser.add_argument('--state', '-s', type=str, help='State code for test data generation (e.g., CA, NY, TX)')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--config', '-c', type=str, default='form_config.json', help='Form configuration file')
    parser.add_argument('--test-data-config', '-t', type=str, default='test_data_config.json', help='Test data configuration file')
    
    args = parser.parse_args()
    
    # Determine headless mode
    headless_mode = args.headless or os.getenv('HEADLESS', 'false').lower() == 'true'
    
    automation = FormAutomation(headless=headless_mode)
    generated_data = {}
    
    try:
        # Generate test data if state code is provided
        if args.state:
            logger.info(f"Generating test data for state: {args.state}")
            generated_data = automation.random_generator.generate_complete_random_person(args.state)
            automation.generated_data = generated_data
            
            if generated_data:
                logger.info("=== FORM AUTOMATION WILL USE THIS DATA ===")
                for key, value in generated_data.items():
                    logger.info(f"  {key}: '{value}'")
                logger.info("=== DATA READY FOR MULTI-PAGE USE ===")
            else:
                logger.warning("Failed to generate test data, proceeding with default values")
        
        # Load configuration
        config_file = args.config
        
        if not os.path.exists(config_file):
            logger.error(f"Configuration file {config_file} not found")
            return
            
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Substitute generated values in configuration
        if generated_data:
            config = automation.substitute_generated_values(config, generated_data)
            
        # Initialize driver
        automation.setup_driver()
        
        # Load the target page
        url = config.get('url')
        if not url:
            logger.error("No URL specified in configuration")
            return
        
        # Check if cookie banner dismissal is configured globally
        dismiss_banner = config.get('dismiss_cookie_banner', True)
        banner_config = config.get('cookie_banner_config')
        
        automation.load_page(url, dismiss_banner, banner_config)
        
        # Fill and submit form
        success = automation.fill_form_from_config(config)
        
        if success:
            logger.info("Form automation completed successfully")
        else:
            logger.warning("Form automation completed with some errors")
            
        # Take screenshot for verification
        automation.take_screenshot("form_completion.png")
        
        # Wait a bit before closing
        time.sleep(3)
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        automation.take_screenshot("error_screenshot.png")
        
    finally:
        automation.close()


if __name__ == "__main__":
    main()