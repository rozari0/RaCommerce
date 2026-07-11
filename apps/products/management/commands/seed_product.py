from django.core.management.base import BaseCommand
import requests
from apps.products.models import Product, Category
from uuid import uuid8
from random import randint


class Command(BaseCommand):
    """A command to seed product into DB"""

    help = "Seeds Dummy Products in Database"

    def handle(self, *args, **options):
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
        print("Done Seeding Products!")
