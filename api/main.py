# api.py
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import toml
from typing import List, Dict
import sys
import os

# Add src directory to Python path to import extract_menu_items
# Adjust this path if your project structure is different
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src') # Assuming src is in the same directory as api.py
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# --- Copied and adapted from src/main.py ---

def load_config():
    """Loads configuration from config.toml"""
    try:
        # Adjust path relative to api.py
        config_path = os.path.join(script_dir, "config.toml")
        return toml.load(config_path)
    except FileNotFoundError:
        # Use default values or raise an error if config is crucial
        print("Warning: config.toml not found. Using default values.", file=sys.stderr)
        return {
            "menu": {
                "wait_timeout": 10,
                "reishauer_url": "https://clients.eurest.ch/reishauer/de/Zahnr%C3%A4dli" # Example default
            }
        }
    except Exception as e:
        raise Exception(f"Error loading configuration: {e}")

config = load_config()
WAIT_TIMEOUT = config["menu"]["wait_timeout"]
REISHAUER_URL = config["menu"]["reishauer_url"]

XPATHS = {
    "menu_items_div": "//tw-menuplan//mat-tab-group//mat-tab-body[contains(@class, 'mat-tab-body-active')]",
    "menu_items": ".//div[contains(@class, 'cols')]" # Relative to menu_items_div
}

def extract_price(price_element):
    """Extracts price string from a price element."""
    try:
        # Find the span containing the price text
        price_span = price_element.find_element(By.TAG_NAME, "span")
        return f"CHF {price_span.text}"
    except Exception:
        return "Price not available"

def extract_menu_items_from_elements(menu_items_elements: List) -> List[Dict[str, str]]:
    """Extracts menu details from a list of Selenium elements."""
    menu_items = []
    for item in menu_items_elements:
        try:
            name = item.find_element(By.TAG_NAME, "h3").text
            description_elements = item.find_elements(By.XPATH, ".//div[contains(@class, 'wide')]//p")
            # Concatenate text from all <p> tags within the description div
            description = "\n".join([p.text for p in description_elements if p.text]).strip()
            # Find the specific price paragraph
            price_wrapper = item.find_element(By.XPATH, ".//div[contains(@class, 'price-wrapper')]//p[contains(@class, 'main')]")
            price = extract_price(price_wrapper)

            # remove comma at end of name
            if name.endswith(','):
                name = name[:-1]

            if name:
                menu_items.append({
                    "name": name,
                    "description": description or "No description", # Provide default if empty
                    "price": price
                })
        except Exception as e:
            print(f"Warning: Could not extract details for a menu item: {e}", file=sys.stderr)
            continue # Skip item if essential parts are missing
    return menu_items

def fetch_menu_data() -> List[Dict[str, str]]:
    """Fetches and extracts menu data using Selenium."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080") # Standard window size

    driver = None # Initialize driver to None
    try:
        # It's recommended to use webdriver_manager or ensure chromedriver is in PATH
        # For simplicity, assuming chromedriver is accessible
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, WAIT_TIMEOUT)

        print(f"Fetching menu from: {REISHAUER_URL}", file=sys.stderr)
        driver.get(REISHAUER_URL)

        # Wait for the active tab body which contains the menu items
        menu_items_div = wait.until(
            EC.visibility_of_element_located((By.XPATH, XPATHS["menu_items_div"]))
        )
        print("Menu container div located.", file=sys.stderr)

        # Find all menu item containers within the active tab
        # Use a relative XPath from the located div for robustness
        menu_items_elements = menu_items_div.find_elements(By.XPATH, XPATHS["menu_items"])
        print(f"Found {len(menu_items_elements)} potential menu item elements.", file=sys.stderr)

        menu_items = extract_menu_items_from_elements(menu_items_elements)
        print(f"Successfully extracted {len(menu_items)} menu items.", file=sys.stderr)
        return menu_items

    except TimeoutException:
        print(f"Error: Timeout waiting for menu elements at {REISHAUER_URL}", file=sys.stderr)
        return [] # Return empty list on timeout
    except Exception as e:
        print(f"An error occurred during menu fetching: {e}", file=sys.stderr)
        return [] # Return empty list on other errors
    finally:
        if driver:
            driver.quit()
            print("Browser closed.", file=sys.stderr)

# --- Flask API ---

app = Flask(__name__)

@app.route('/menu', methods=['GET'])
def get_menu():
    """API endpoint to get the current menu."""
    menu_data = fetch_menu_data()
    if not menu_data:
        # Return 500 or appropriate status if fetching failed or no menu found
        return jsonify({"error": "Could not retrieve menu data or no menu items found."}), 500
    return jsonify(menu_data)

if __name__ == '__main__':
    # Runs the Flask development server
    # For production, use a WSGI server like Gunicorn or uWSGI
    app.run(debug=True, host='0.0.0.0', port=5001) # Use a different port if 5000 is common
