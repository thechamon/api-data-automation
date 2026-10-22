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