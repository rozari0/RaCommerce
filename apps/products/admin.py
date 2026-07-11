from django.contrib import admin

from .models import Category, Product

admin.site.register([Product, Category])
admin.site.site_header = "RaCommerce Admin"
