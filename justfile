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

test:
    (cd apps ; python ../manage.py test)

redis:
    docker run --name djredis -d -p 6379:6379 --rm redis
