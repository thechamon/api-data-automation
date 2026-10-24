
import csv
import json

import pytest

from reports import (
    write_report_to_file,
    write_csv_report,
    write_summary_csv,
)


def test_write_report_to_file_creates_valid_json(sample_products, tmp_path):
    """JSON report তৈরি হয় এবং তার content সঠিক থাকে কি না পরীক্ষা করে।"""

    # Temporary directory-তে JSON file-এর path তৈরি করছি।
    filename = tmp_path / "reports" / "products.json"

    # Function-টি দিয়ে JSON report লিখছি।
    write_report_to_file(sample_products, filename)

    # File তৈরি হয়েছে কি না পরীক্ষা করছি।
    assert filename.exists()

    # লেখা JSON file আবার পড়ে Python data-তে রূপান্তর করছি।
    with filename.open("r", encoding="utf-8") as file:
        saved_products = json.load(file)

    # Saved data মূল products data-এর সমান কি না পরীক্ষা করছি।
    assert saved_products == sample_products


def test_write_report_to_file_handles_empty_products(tmp_path):
    """Empty product list দিলেও valid JSON report তৈরি হয় কি না পরীক্ষা করে।"""

    # Empty list-এর report রাখার জন্য temporary path তৈরি করছি।
    filename = tmp_path / "empty.json"

    # Empty product list দিয়ে JSON report লিখছি।
    write_report_to_file([], filename)

    # File তৈরি হয়েছে এবং তার content empty list কি না পরীক্ষা করছি।
    assert filename.exists()
    with filename.open("r", encoding="utf-8") as file:
        assert json.load(file) == []


def test_write_csv_report_creates_valid_csv(sample_products, tmp_path):
    """Products CSV-তে সঠিক header এবং product rows লেখা হয় কি না পরীক্ষা করে।"""

    # Temporary directory-তে CSV file-এর path তৈরি করছি।
    filename = tmp_path / "reports" / "products.csv"

    # Function-টি দিয়ে CSV report লিখছি।
    write_csv_report(sample_products, filename)

    # CSV file তৈরি হয়েছে কি না পরীক্ষা করছি।
    assert filename.exists()

    # CSV file পড়ে rows-এর তালিকা তৈরি করছি।
    with filename.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    # CSV-তে product-এর সংখ্যা ঠিক আছে কি না পরীক্ষা করছি।
    assert len(rows) == len(sample_products)

    # CSV-র প্রথম product-এর গুরুত্বপূর্ণ field সঠিক কি না পরীক্ষা করছি।
    assert rows[0]["id"] == str(sample_products[0]["id"])
    assert rows[0]["name"] == sample_products[0]["name"]
    assert rows[0]["brand"] == sample_products[0]["brand"]
    assert float(rows[0]["price"]) == sample_products[0]["price"]


def test_write_csv_report_handles_empty_products(tmp_path):
    """Empty product list দিলেও header-সহ CSV তৈরি হয় কি না পরীক্ষা করে।"""

    # Empty CSV report-এর জন্য temporary path তৈরি করছি।
    filename = tmp_path / "empty.csv"

    # Empty product list দিয়ে CSV report লিখছি।
    write_csv_report([], filename)

    # CSV file তৈরি হয়েছে কি না পরীক্ষা করছি।
    assert filename.exists()

    # CSV file-এর header পড়ছি।
    with filename.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Header থাকবে, কিন্তু কোনো product row থাকবে না।
    assert rows[0] == [
        "id", "name", "brand", "price",
        "rating", "category", "width", "barcode"
    ]
    assert len(rows) == 1


def test_write_summary_csv_creates_valid_report(tmp_path):
    """Summary CSV-তে overall metrics এবং category statistics লেখা হয় কি না পরীক্ষা করে।"""

    # Summary report-এর জন্য sample summary data তৈরি করছি।
    summary = {
        "total_products": 3,
        "average_price": 200.0,
        "categories_count": 2,
        "min_price_product": {"name": "Product A", "price": 100},
        "max_price_product": {"name": "Product C", "price": 300},
        "category_stats": {
            "beauty": {"count": 2, "average_price": 150.0},
            "furniture": {"count": 1, "average_price": 300.0},
        },
    }

    # Temporary directory-তে summary CSV-এর path তৈরি করছি।
    filename = tmp_path / "reports" / "summary.csv"

    # Function-টি দিয়ে summary report লিখছি।
    write_summary_csv(summary, filename)

    # Summary file তৈরি হয়েছে কি না পরীক্ষা করছি।
    assert filename.exists()

    # CSV file-এর সব row পড়ছি।
    with filename.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.reader(file))

    # Overall metrics-এর header এবং values সঠিক কি না পরীক্ষা করছি।
    assert rows[0] == ["Metric", "Value"]
    assert rows[1] == ["Total Products", "3"]
    assert rows[2] == ["Average Price", "200.0"]
    assert rows[3] == ["Categories Count", "2"]

    # Minimum ও maximum price product সঠিকভাবে লেখা হয়েছে কি না পরীক্ষা করছি।
    assert rows[4] == ["Min Price Product", "Product A ($100)"]
    assert rows[5] == ["Max Price Product", "Product C ($300)"]

    # Blank row-এর পরে category table-এর header ও data পরীক্ষা করছি।
    assert rows[7] == ["Category", "Count", "Average Price"]
    assert rows[8] == ["beauty", "2", "150.0"]
    assert rows[9] == ["furniture", "1", "300.0"]


def test_write_report_to_file_raises_for_invalid_json_data(tmp_path):
    """JSON-এ serialize করা যায় না এমন data দিলে TypeError ওঠে কি না পরীক্ষা করে।"""

    # JSON file-এর temporary path তৈরি করছি।
    filename = tmp_path / "invalid.json"

    # Python-এর set JSON-এ সরাসরি serialize করা যায় না।
    invalid_products = [{"name": "Product A", "tags": {"new", "sale"}}]

    # Function exception-টি চেপে না রেখে বাইরে পাঠায় কি না পরীক্ষা করছি।
    with pytest.raises(TypeError):
        write_report_to_file(invalid_products, filename)
