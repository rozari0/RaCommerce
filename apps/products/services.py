from django.core.cache import cache

from .models import Category, Product


def get_all_descendants(start_id):
    """DFS implementation"""

    cache_key = f"descendants_of_{start_id}"
    cached_result = cache.get(cache_key)

    if cached_result:
        return cached_result

    all_categories = Category.objects.all().values("id", "parent_id")

    tree = {}

    for category in all_categories:
        parent_id = category["parent_id"]
        if parent_id not in tree:
            tree[parent_id] = []
        tree[parent_id].append(category["id"])

    stack = tree.get(start_id, []).copy()

    desc_ids = []

    while stack:
        current_id = stack.pop()
        desc_ids.append(current_id)

        if current_id in tree:
            stack.extend(tree.get(current_id))

    cache.set(cache_key, desc_ids, timeout=60 * 5)

    return desc_ids


def get_related_products(category_id, limit=50):
    category_ids = category_id + get_all_descendants(category_id)

    products = Product.objects.filter(
        category_id__in=category_ids, status=Product.STATUS_CHOICES.ACTIVE, stock__gt=0
    ).order_by("created_at")[:limit]

    return products
