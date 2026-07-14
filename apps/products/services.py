from django.core.cache import cache


def get_all_descendants(start_id):
    """DFS implementation"""
    from .models import Category

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
