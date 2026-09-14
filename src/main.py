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
# print(len(products))
# print(products[0]["brand"])
# print(products[0]["dimensions"]["width"])
# print(products[0]["meta"]["barcode"])


# product = products[0]
# product = products[15]

def transform_product(product):
    clean_product = {
        "id": product["id"],
        "name": product["title"],
        "brand": product.get("brand", "Unknown"),
        "price": product["price"],
        "rating": product["rating"],
        "category": product["category"],
        "width": product["dimensions"]["width"],
        "barcode": product["meta"]["barcode"]
    }

    return clean_product

clean_products = [transform_product(product) for product in products]

# print(len(clean_products)) 
# print(clean_products[15])



# expensive_products = []

# for product in clean_products:
#     if product["price"] > 100:
#         expensive_products.append(product)



expensive_products = [
    product for product in clean_products
    if product["price"] > 100
]


# print(len(expensive_products))
# print(expensive_products[0])





high_value_products = []

for product in clean_products:
    if product["price"] > 100 and product["rating"] > 4.5:
        high_value_products.append(product)


# print(len(high_value_products))
# print(high_value_products[0])


sorted_products = sorted(
    clean_products,
    key=lambda product: product["rating"], 
    reverse=True
)

# print(len(sorted_products))
# print(sorted_products[:5])


min_price = min(
    clean_products,
    key=lambda product: product["price"]
)

# print(f"{min_price['name']} is minimum priced product with ${min_price['price']}")


max_price = max(
    clean_products,
    key=lambda product: product["price"]
)

# print(f"{max_price['name']} is maximum priced product with ${max_price['price']}")

prices = [product["price"] for product in clean_products]
total_price = sum(prices)
avarage_price = total_price / len(clean_products)
# print(f"Average price: ${avarage_price:.2f}")



category_counts = {}

for product in clean_products:
    category = product["category"]
    if category in category_counts:
        category_counts[category] += 1
    else:
        category_counts[category] = 1

print(category_counts)