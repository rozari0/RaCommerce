dev:
    uv run manage.py runserver

makemigrations:
    uv run manage.py makemigrations

migrate:
    uv run manage.py migrate

# Format python files.
format:
    uv run ruff check --select I --fix
    uv run ruff format .
