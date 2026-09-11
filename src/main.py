import requests
import logging
import os

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


def fetch_data_from_api( skip, limit):
    try:
        response = requests.get(f"{API_URL}/products?limit={limit}&skip={skip}", timeout=10)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        data = response.json()
        return data
    
    except requests.exceptions.HTTPError as e:
        logging.warning(f"HTTP error {e}")
        return None

    except requests.exceptions.Timeout as e:
        logging.warning(f"Connection timeout {e}")
        return None

    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"Invalid data structure {e}")
        return None
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching product data: {e}")
        return None


data = fetch_data_from_api(0, 30)



# prgination


all_products = []

def fetch_all_products():
    if data is not None:
        skip = data["limit"]
        all_products.extend(data["products"])
        while skip < data["total"]:
            page_data = fetch_data_from_api(skip, data["limit"])
            if page_data is not None:
                all_products.extend(page_data["products"])

            skip = skip + data["limit"]
    return all_products



products = fetch_all_products()
print(len(products))