import pytest


@pytest.fixture
def sample_products():
    """
    Return two sample products for testing analytics and transformations.

    The data follows the cleaned product structure used by this project.
    """
    return [
        {
            "id": 1,
            "name": "Product A",
            "brand": "Brand A",
            "price": 100.0,
            "rating": 4.5,
            "category": "beauty",
            "width": 10,
            "barcode": "BARCODE001",
        },
        {
            "id": 2,
            "name": "Product B",
            "brand": "Brand B",
            "price": 200.0,
            "rating": 4.0,
            "category": "beauty",
            "width": 20,
            "barcode": "BARCODE002",
        },
    ]


@pytest.fixture
def category_products():
    """
    Return products from two categories for category-statistics tests.

    The fixture contains two beauty products and one furniture product.
    """
    return [
        {
            "id": 1,
            "name": "Product A",
            "brand": "Brand A",
            "price": 100.0,
            "rating": 4.5,
            "category": "beauty",
            "width": 10,
            "barcode": "BARCODE001",
        },
        {
            "id": 2,
            "name": "Product B",
            "brand": "Brand B",
            "price": 200.0,
            "rating": 4.0,
            "category": "beauty",
            "width": 20,
            "barcode": "BARCODE002",
        },
        {
            "id": 3,
            "name": "Product C",
            "brand": "Brand C",
            "price": 300.0,
            "rating": 4.8,
            "category": "furniture",
            "width": 30,
            "barcode": "BARCODE003",
        },
    ]


@pytest.fixture
def empty_products():
    """
    Return an empty product list for testing empty-input behavior.
    """
    return []