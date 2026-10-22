import json
import csv
import requests
import logging
import os
import time

from pathlib import Path
from dotenv import load_dotenv



BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR/ ".env")  # Load environment variables from .env file

API_URL = os.getenv("API_URL")

LOG_FILE = BASE_DIR / "app.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
    force=True
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



category_stats = {}

for product in clean_products:
    category = product["category"]

    if category not in category_stats:
        category_stats[category] = {
            "count": 0,
            "total_price": 0
        }

    category_stats[category]["count"] += 1
    category_stats[category]["total_price"] += product["price"]


for category, stats in category_stats.items():
    count = stats["count"]
    total_price = stats["total_price"]
    average_price = total_price / count if count > 0 else 0
    # print(f"{category}: ${average_price:.2f}")



def filter_products(products, min_price=None, min_rating=None):
    filtered_products = [
        product for product in products
        if (min_price is None or product["price"] >= min_price)
        and (min_rating is None or product["rating"] >= min_rating)
    ]
    return filtered_products


# Filter by price
expensive_products = filter_products(clean_products, min_price=100)

# Filter by rating
top_rated_products = filter_products(clean_products, min_rating=4.5)

# Filter by both price and rating
high_value_products = filter_products(
    clean_products,
    min_price=100,
    min_rating=4.5
)




def write_report_to_file(products, filename):
    file_path = Path(filename)

    try:
        # Create directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON report
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(products, file, indent=4, ensure_ascii=False)

        logging.info(
            "JSON report generated successfully: %s | Products: %d",
            file_path,
            len(products)
        )

    except (OSError, TypeError, ValueError) as e:
        logging.exception("Failed to generate JSON report: %s", file_path)
        raise


REPORTS_DIR = BASE_DIR / "reports"
JSON_REPORT = REPORTS_DIR / "products.json"

write_report_to_file(clean_products, JSON_REPORT)


def write_csv_report(products, filename):
    file_path = Path(filename)

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as file:
            fieldnames = [
                "id",
                "name",
                "brand",
                "price",
                "rating",
                "category",
                "width",
                "barcode"
            ]

            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)

        logging.info(
            "CSV report generated successfully: %s | Products: %d",
            file_path,
            len(products)
        )

    except (OSError, TypeError, ValueError, csv.Error):
        logging.exception("Failed to generate CSV report: %s", file_path)
        raise


write_csv_report(clean_products, REPORTS_DIR / "products.csv")