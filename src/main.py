from pathlib import Path

from api_client import fetch_all_products
from transformer import transform_product
from analytics import generate_summary
from reports import (
    write_report_to_file,
    write_csv_report,
    write_summary_csv,
)


BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"

JSON_REPORT = REPORTS_DIR / "products.json"
PRODUCTS_CSV_REPORT = REPORTS_DIR / "products.csv"
SUMMARY_CSV_REPORT = REPORTS_DIR / "summary.csv"


def main():
    # 1. Fetch raw products from the API
    products = fetch_all_products()

    # 2. Transform raw products into clean data
    clean_products = [
        transform_product(product)
        for product in products
    ]

    # 3. Generate summary statistics
    summary = generate_summary(clean_products)

    # 4. Prepare the JSON report
    report_data = {
        "summary": summary,
        "products": clean_products,
    }

    # 5. Export reports
    write_report_to_file(report_data, JSON_REPORT)
    write_csv_report(clean_products, PRODUCTS_CSV_REPORT)
    write_summary_csv(summary, SUMMARY_CSV_REPORT)


if __name__ == "__main__":
    main()