python manage.py migrate
python manage.py seed_users && python manage.py seed_product
gunicorn --workers=2 -b 0.0.0.0:8000 config.wsgi
