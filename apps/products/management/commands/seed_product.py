from random import randint
from uuid import uuid8

import requests
from django.core.management.base import BaseCommand

from apps.products.models import Category, Product


class Command(BaseCommand):
    """A command to seed product into DB"""

    help = "Seeds Dummy Products in Database"

    def handle(self, *args, **options):
        if Product.objects.exists():
            print("Products already seeded!")
            return
        products = requests.get("https://fakestoreapi.com/products").json()

        for product in products:
            category, _ = Category.objects.get_or_create(
                name=product.get("category").capitalize()
            )
            Product.objects.get_or_create(
                name=product.get("title"),
                category=category,
                description=product.get("description"),
                defaults={
                    "stock": randint(5, 100),
                    "price": product.get("price"),
                    "sku": str(uuid8()).split("-")[0],
                },
            )

        # Custom Product to show DFS
        category, _ = Category.objects.get_or_create(name="Custom")
        Product.objects.get_or_create(
            name="Custom Product",
            category=category,
            description="This is a custom product for testing purposes.",
            defaults={
                "stock": 50,
                "price": 99.99,
                "sku": str(uuid8()).split("-")[0],
            },
        )
        electronics_category, _ = Category.objects.get_or_create(name="Electronics")
        electronics_category.parent = category
        electronics_category.save()

        print("Done Seeding Products!")
