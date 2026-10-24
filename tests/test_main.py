
from unittest.mock import patch, call

import main


def test_main_runs_complete_workflow(sample_products):
    """API থেকে data আনা থেকে শুরু করে তিনটি report লেখার workflow পরীক্ষা করে।"""

    # API থেকে raw products পাওয়া যাচ্ছে—এমন পরিস্থিতি তৈরি করছি।
    with patch("main.fetch_all_products", return_value=[
        {
            "id": 1,
            "title": "Product A",
            "brand": "Brand A",
            "price": 100,
            "rating": 4.5,
            "category": "beauty",
            "dimensions": {"width": 10},
            "meta": {"barcode": "111"},
        },
        {
            "id": 2,
            "title": "Product B",
            "brand": "Brand B",
            "price": 200,
            "rating": 4.0,
            "category": "beauty",
            "dimensions": {"width": 20},
            "meta": {"barcode": "222"},
        },
    ]) as mock_fetch, \
         patch("main.transform_product", side_effect=sample_products) as mock_transform, \
         patch("main.generate_summary", return_value={"total_products": 2}) as mock_summary, \
         patch("main.write_report_to_file") as mock_json_report, \
         patch("main.write_csv_report") as mock_products_csv, \
         patch("main.write_summary_csv") as mock_summary_csv:

        # main() চালিয়ে পুরো workflow execute করছি।
        main.main()

        # API function-টি ঠিক একবার call হয়েছে কি না পরীক্ষা করছি।
        mock_fetch.assert_called_once_with()

        # প্রতিটি raw product transform করা হয়েছে কি না পরীক্ষা করছি।
        assert mock_transform.call_count == 2

        # Transformed products দিয়েই summary তৈরি হয়েছে কি না পরীক্ষা করছি।
        mock_summary.assert_called_once_with(sample_products)

        # JSON report সঠিক data এবং destination path-এ পাঠানো হয়েছে কি না পরীক্ষা করছি।
        mock_json_report.assert_called_once_with(
            {
                "summary": {"total_products": 2},
                "products": sample_products,
            },
            main.JSON_REPORT,
        )

        # Products CSV সঠিক data এবং destination path-এ পাঠানো হয়েছে কি না পরীক্ষা করছি।
        mock_products_csv.assert_called_once_with(
            sample_products,
            main.PRODUCTS_CSV_REPORT,
        )

        # Summary CSV-তে summary এবং সঠিক destination path পাঠানো হয়েছে কি না পরীক্ষা করছি।
        mock_summary_csv.assert_called_once_with(
            {"total_products": 2},
            main.SUMMARY_CSV_REPORT,
        )


def test_main_handles_empty_api_response():
    """API থেকে empty list এলে main() empty data নিয়েও workflow চালায় কি না পরীক্ষা করে।"""

    # API কোনো product ফেরত দেয়নি—এমন পরিস্থিতি তৈরি করছি।
    with patch("main.fetch_all_products", return_value=[]) as mock_fetch, \
         patch("main.transform_product") as mock_transform, \
         patch("main.generate_summary", return_value={"total_products": 0}) as mock_summary, \
         patch("main.write_report_to_file") as mock_json_report, \
         patch("main.write_csv_report") as mock_products_csv, \
         patch("main.write_summary_csv") as mock_summary_csv:

        # Empty API response নিয়ে main workflow চালাচ্ছি।
        main.main()

        # API call হয়েছে কি না পরীক্ষা করছি।
        mock_fetch.assert_called_once_with()

        # Product না থাকায় transform function call হওয়ার কথা নয়।
        mock_transform.assert_not_called()

        # Empty list দিয়েই summary তৈরি হয়েছে কি না পরীক্ষা করছি।
        mock_summary.assert_called_once_with([])

        # JSON report-এ empty products list এবং summary পাঠানো হয়েছে কি না পরীক্ষা করছি।
        mock_json_report.assert_called_once_with(
            {
                "summary": {"total_products": 0},
                "products": [],
            },
            main.JSON_REPORT,
        )

        # Empty products list-সহ CSV report function call হয়েছে কি না পরীক্ষা করছি।
        mock_products_csv.assert_called_once_with(
            [],
            main.PRODUCTS_CSV_REPORT,
        )

        # Empty data-এর summary-সহ summary CSV function call হয়েছে কি না পরীক্ষা করছি।
        mock_summary_csv.assert_called_once_with(
            {"total_products": 0},
            main.SUMMARY_CSV_REPORT,
        )
