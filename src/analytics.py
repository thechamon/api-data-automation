def filter_products(products, min_price=None, min_rating=None):
    filtered_products = [
        product for product in products
        if (min_price is None or product["price"] >= min_price)
        and (min_rating is None or product["rating"] >= min_rating)
    ]
    return filtered_products



def generate_summary(products):
    total_products = len(products)

    if not products:
        return {
            "total_products": 0,
            "average_price": 0,
            "categories_count": 0,
            "min_price_product": None,
            "max_price_product": None,
            "category_stats": {},
        }

    total_price = sum(product["price"] for product in products)
    average_price = total_price / total_products if total_products > 0 else 0
    min_price_product = min(
        products,
        key=lambda product: product["price"]
    )

    max_price_product = max(
        products,
        key=lambda product: product["price"]
    )

    category_stats = {}

    for product in products:
        category = product["category"]

        if category not in category_stats:
            category_stats[category] = {
                "count": 0,
                "total_price": 0
            }

        category_stats[category]["count"] += 1
        category_stats[category]["total_price"] += product["price"]

    for stats in category_stats.values():
        stats["average_price"] = round(
            stats["total_price"] / stats["count"], 2
        )
        del stats["total_price"]

    return {
        "total_products": total_products,
        "average_price": round(average_price, 2),
        "categories_count": len(category_stats),
        "min_price_product": {
            "name": min_price_product["name"],
            "price": min_price_product["price"]
        },
        "max_price_product": {
            "name": max_price_product["name"],
            "price": max_price_product["price"]
        },
        "category_stats": category_stats
    }





def sort_products(products, sort_by="rating", descending=True):
    return sorted(
        products,
        key=lambda product: product[sort_by],
        reverse=descending
    )