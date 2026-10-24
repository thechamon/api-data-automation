"""
Unit tests for the analytics module.

These tests verify product counts, category counts, average prices,
minimum and maximum priced products, and category-level statistics.
"""

from analytics import generate_summary


def test_generate_summary_counts_products(sample_products):
    """Verify total product count and average price."""

    # Generate summary statistics using the sample product data.
    result = generate_summary(sample_products)

    # Verify that both products are included in the total count.
    assert result["total_products"] == 2

    # Verify that the average price of 100 and 200 is 150.
    assert result["average_price"] == 150


def test_generate_summary_counts_categories(sample_products):
    """Verify that unique product categories are counted correctly."""

    # Generate summary statistics for the sample products.
    result = generate_summary(sample_products)

    # Both sample products belong to "beauty", so there is one unique category.
    assert result["categories_count"] == 1


def test_generate_summary_with_empty_products(empty_products):
    """Verify that empty input produces valid zero-value statistics."""

    # Generate summary statistics using an empty product list.
    result = generate_summary(empty_products)

    # Verify that the total product count is zero.
    assert result["total_products"] == 0

    # Verify that the average price is zero when no products exist.
    assert result["average_price"] == 0

    # Verify that no product categories are counted.
    assert result["categories_count"] == 0

    # Verify that no minimum-priced product exists for empty input.
    assert result["min_price_product"] is None

    # Verify that no maximum-priced product exists for empty input.
    assert result["max_price_product"] is None

    # Verify that category statistics are empty when there are no products.
    assert result["category_stats"] == {}


def test_generate_summary_finds_min_and_max_price_products(sample_products):
    """Verify that the cheapest and most expensive products are identified."""

    # Calculate summary statistics for the sample products.
    result = generate_summary(sample_products)

    # Product A costs 100, making it the cheapest product.
    assert result["min_price_product"]["name"] == "Product A"

    # Product B costs 200, making it the most expensive product.
    assert result["max_price_product"]["name"] == "Product B"


def test_generate_summary_category_stats_counts_products(category_products):
    """Verify product counts and average prices for each category."""

    # Generate category-level statistics for products from different categories.
    result = generate_summary(category_products)

    # Verify that two products belong to the beauty category.
    assert result["category_stats"]["beauty"]["count"] == 2

    # Verify that one product belongs to the furniture category.
    assert result["category_stats"]["furniture"]["count"] == 1

    # Verify that the average beauty product price is (100 + 200) / 2 = 150.
    assert result["category_stats"]["beauty"]["average_price"] == 150

    # Verify that the furniture category's average price is 300.
    assert result["category_stats"]["furniture"]["average_price"] == 300