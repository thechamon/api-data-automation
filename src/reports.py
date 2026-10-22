import json
import csv
import logging

from pathlib import Path



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




# write_report_to_file(clean_products, JSON_REPORT)


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


# write_csv_report(clean_products, REPORTS_DIR / "products.csv")






def write_summary_csv(summary, filename):
    file_path = Path(filename)

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Total Products", summary["total_products"]])
            writer.writerow(["Average Price", summary["average_price"]])
            writer.writerow(["Categories Count", summary["categories_count"]])
            writer.writerow([
                "Min Price Product",
                f"{summary['min_price_product']['name']} (${summary['min_price_product']['price']})"
            ])
            writer.writerow([
                "Max Price Product",
                f"{summary['max_price_product']['name']} (${summary['max_price_product']['price']})"
            ])

            writer.writerow([])
            writer.writerow(["Category", "Count", "Average Price"])
            for category, stats in summary["category_stats"].items():
                writer.writerow([category, stats["count"], stats["average_price"]])

        logging.info(
            "Summary CSV report generated successfully: %s",
            file_path
        )

    except (OSError, TypeError, ValueError, csv.Error):
        logging.exception("Failed to generate summary CSV report: %s", file_path)
        raise





