#!/usr/bin/env python3
"""
Test Data Generator Module
Generates test data by visiting a test data generation page and extracting values.
"""

import time
import json
import logging
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import os

logger = logging.getLogger(__name__)


class TestDataGenerator:
    def __init__(self, headless: bool = True, timeout: int = 10):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        self.generated_data = {}
        
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
        
        logger.info("Test Data Generator WebDriver initialized successfully")
        
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
                {"selector_type": "xpath", "selector": "//button[contains(text(), 'Got it')]"}
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

    def load_generator_page(self, url: str, dismiss_banner: bool = True, banner_config: Optional[Dict] = None):
        """Load the test data generator page"""
        try:
            self.driver.get(url)
            logger.info(f"Successfully loaded test data generator page: {url}")
            time.sleep(2)
            
            # Try to dismiss cookie banner if requested
            if dismiss_banner:
                self.dismiss_cookie_banner(banner_config)
                
        except Exception as e:
            logger.error(f"Failed to load generator page {url}: {str(e)}")
            raise
            
    def select_state(self, state_code: str, dropdown_config: Dict):
        """Select state from dropdown"""
        try:
            selector = dropdown_config.get('selector')
            selector_type = dropdown_config.get('selector_type', 'id')
            
            by_type = getattr(By, selector_type.upper())
            element = self.wait.until(EC.presence_of_element_located((by_type, selector)))
            select = Select(element)
            select.select_by_value(state_code)
            logger.info(f"Selected state: {state_code}")
            return True
        except TimeoutException:
            logger.error(f"State dropdown {selector} not found")
            return False
        except Exception as e:
            logger.error(f"Error selecting state {state_code}: {str(e)}")
            return False
            
    def click_generate_button(self, button_config: Dict):
        """Click the generate button"""
        try:
            selector = button_config.get('selector')
            selector_type = button_config.get('selector_type', 'id')
            
            by_type = getattr(By, selector_type.upper())
            element = self.wait.until(EC.element_to_be_clickable((by_type, selector)))
            element.click()
            logger.info("Clicked generate button")
            return True
        except TimeoutException:
            logger.error(f"Generate button {selector} not found or not clickable")
            return False
        except Exception as e:
            logger.error(f"Error clicking generate button: {str(e)}")
            return False
            
    def extract_generated_data(self, output_fields: Dict, wait_config: Optional[Dict] = None):
        """Extract the generated data from the page"""
        try:
            # Wait for generation to complete if configured
            if wait_config:
                wait_selector = wait_config.get('selector')
                wait_selector_type = wait_config.get('selector_type', 'id')
                wait_timeout = wait_config.get('timeout', 30)
                
                by_type = getattr(By, wait_selector_type.upper())
                WebDriverWait(self.driver, wait_timeout).until(
                    EC.presence_of_element_located((by_type, wait_selector))
                )
                logger.info("Generation completed, extracting data")
            
            extracted_data = {}
            
            for field_name, field_config in output_fields.items():
                try:
                    selector = field_config.get('selector')
                    selector_type = field_config.get('selector_type', 'id')
                    
                    by_type = getattr(By, selector_type.upper())
                    element = self.wait.until(EC.presence_of_element_located((by_type, selector)))
                    
                    # Get the value (try value attribute first, then text content)
                    value = element.get_attribute('value') or element.text
                    extracted_data[field_name] = value
                    logger.info(f"Extracted {field_name}: {value}")
                    
                except Exception as e:
                    logger.error(f"Failed to extract {field_name}: {str(e)}")
                    extracted_data[field_name] = None
            
            self.generated_data = extracted_data
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting generated data: {str(e)}")
            return {}
            
    def generate_test_data(self, state_code: str, config_file: str = "test_data_config.json"):
        """Main method to generate test data"""
        try:
            # Load configuration
            if not os.path.exists(config_file):
                logger.error(f"Test data configuration file {config_file} not found")
                return {}
                
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            gen_config = config.get('test_data_generation', {})
            
            if not gen_config.get('enabled', True):
                logger.info("Test data generation is disabled")
                return {}
            
            # Setup driver
            self.setup_driver()
            
            # Load generator page
            url = gen_config.get('url')
            if not url:
                logger.error("No generator URL specified in configuration")
                return {}
            
            dismiss_banner = gen_config.get('dismiss_cookie_banner', True)
            banner_config = gen_config.get('cookie_banner_config')
            
            self.load_generator_page(url, dismiss_banner, banner_config)
            
            # Select state
            state_dropdown_config = gen_config.get('state_dropdown', {})
            if not self.select_state(state_code, state_dropdown_config):
                logger.error("Failed to select state")
                return {}
            
            # Click generate button
            generate_button_config = gen_config.get('generate_button', {})
            if not self.click_generate_button(generate_button_config):
                logger.error("Failed to click generate button")
                return {}
            
            # Wait for generation
            wait_time = gen_config.get('wait_time_after_generate', 3)
            time.sleep(wait_time)
            
            # Extract generated data
            output_fields = gen_config.get('output_fields', {})
            wait_config = gen_config.get('wait_for_generation')
            
            generated_data = self.extract_generated_data(output_fields, wait_config)
            
            logger.info(f"Successfully generated test data: {generated_data}")
            return generated_data
            
        except Exception as e:
            logger.error(f"Error generating test data: {str(e)}")
            return {}
        finally:
            self.close()
            
    def close(self):
        """Close the browser and clean up"""
        if self.driver:
            self.driver.quit()
            logger.info("Test Data Generator browser closed")


def generate_test_data_for_state(state_code: str, config_file: str = "test_data_config.json", headless: bool = True):
    """Convenience function to generate test data for a given state"""
    generator = TestDataGenerator(headless=headless)
    return generator.generate_test_data(state_code, config_file)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_data_generator.py <state_code>")
        print("Example: python test_data_generator.py CA")
        sys.exit(1)
    
    state_code = sys.argv[1]
    data = generate_test_data_for_state(state_code, headless=False)
    print(f"Generated data for {state_code}: {data}")