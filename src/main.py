import requests
import logging
import os
import time

from pathlib import Path
from dotenv import load_dotenv



BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR/ ".env")  # Load environment variables from .env file

API_URL = os.getenv("API_URL")

logging.basicConfig(
    filename='app.log',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def fetch_data_from_api( skip, limit, max_retries = 3):

    attempt = 0
    page_number = (skip // limit) + 1

    while attempt <= max_retries:
        try:
            response = requests.get(f"{API_URL}/products?limit={limit}&skip={skip}", timeout=10)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

            data = response.json()
            if attempt > 0:
                logging.info(
                    f"Page {page_number} fetched successfully after {attempt} retries"
                )
            return data
        
        except requests.exceptions.HTTPError as e:
            logging.warning(f"HTTP error {e}")
            return None

        except requests.exceptions.Timeout as e:
            logging.warning(f"Connection timeout {e}")
            attempt += 1
            if attempt <= max_retries:
                logging.warning(
                    f"Timeout on page {page_number}. "
                    f"Retrying attempt {attempt}/{max_retries}"
                )
                time.sleep(2 ** attempt)
            else:
                logging.error(
                    f"Page {page_number} (skip={skip}): "
                    f"API request failed after {max_retries} retries due to timeout"
                )
                return None

        except requests.exceptions.JSONDecodeError as e:
            logging.error(f"Invalid data structure {e}")
            return None
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching product data: {e}")
            return None





# pagination



def fetch_all_products():
    all_products = []
    data = fetch_data_from_api(0, 30)
    if data is not None and "products" in data and data["products"] and "limit" in data and "skip" in data and "total" in data:
        skip = data["limit"]
        all_products.extend(data["products"])
        while skip < data["total"]:
            page_data = fetch_data_from_api(skip, data["limit"])
            if page_data is not None and "products" in page_data and page_data["products"] and "limit" in page_data and "skip" in page_data and "total" in page_data:
                all_products.extend(page_data["products"])
                skip = skip + page_data["limit"]
            else:
                logging.error(f"Failed to fetch page with skip={skip}. Stopping pagination.")
                break
    return all_products



products = fetch_all_products()
print(len(products))