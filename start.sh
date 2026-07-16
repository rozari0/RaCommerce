python manage.py seed_users && python manage.py seed_products
python manage.py migrate && gunicorn --workers=2 -b 0.0.0.0:8000 config.wsgi
