"""
Unit tests for the transformer module.

These tests verify field mapping, default brand handling,
nested field extraction, and missing-field errors.
"""

import pytest

from transformer import transform_product


def test_transform_product_maps_all_fields():
    # Testing whether all required fields are mapped to the correct output keys.
    product = {
        "id": 1,
        "title": "Test Product",
        "brand": "Test Brand",
        "price": 100,
        "rating": 4.5,
        "category": "beauty",
        "dimensions": {"width": 10},
        "meta": {"barcode": "TEST123"},
    }

    result = transform_product(product)

    assert result == {
        "id": 1,
        "name": "Test Product",
        "brand": "Test Brand",
        "price": 100,
        "rating": 4.5,
        "category": "beauty",
        "width": 10,
        "barcode": "TEST123",
    }


def test_transform_product_uses_unknown_when_brand_is_missing():
    # Testing whether the default brand value is "Unknown" when brand is absent.
    product = {
        "id": 2,
        "title": "Product Without Brand",
        "price": 50,
        "rating": 4.0,
        "category": "beauty",
        "dimensions": {"width": 12},
        "meta": {"barcode": "TEST456"},
    }

    result = transform_product(product)

    assert result["brand"] == "Unknown"


def test_transform_product_extracts_nested_fields():
    # Testing whether width and barcode are extracted from nested dictionaries.
    product = {
        "id": 3,
        "title": "Nested Data Product",
        "brand": "Example Brand",
        "price": 75,
        "rating": 4.2,
        "category": "furniture",
        "dimensions": {"width": 25},
        "meta": {"barcode": "NESTED789"},
    }

    result = transform_product(product)

    assert result["width"] == 25
    assert result["barcode"] == "NESTED789"


def test_transform_product_raises_key_error_when_required_field_is_missing():
    # Testing whether a missing required top-level field raises KeyError.
    product = {
        "title": "Incomplete Product",
        "brand": "Example Brand",
        "price": 50,
        "rating": 4.0,
        "category": "beauty",
        "dimensions": {"width": 10},
        "meta": {"barcode": "TEST000"},
    }

    with pytest.raises(KeyError):
        transform_product(product)


def test_transform_product_raises_key_error_when_width_is_missing():
    # Testing whether missing dimensions.width raises KeyError.
    product = {
        "id": 4,
        "title": "Missing Width",
        "brand": "Example Brand",
        "price": 80,
        "rating": 4.1,
        "category": "furniture",
        "dimensions": {},
        "meta": {"barcode": "WIDTH001"},
    }

    with pytest.raises(KeyError):
        transform_product(product)


def test_transform_product_raises_key_error_when_barcode_is_missing():
    # Testing whether missing meta.barcode raises KeyError.
    product = {
        "id": 5,
        "title": "Missing Barcode",
        "brand": "Example Brand",
        "price": 90,
        "rating": 4.3,
        "category": "beauty",
        "dimensions": {"width": 15},
        "meta": {},
    }

    with pytest.raises(KeyError):
        transform_product(product)