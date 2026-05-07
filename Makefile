.PHONY: dev start build ruff-config lint lint-check lint-types format format-check test test-cov check db-migrate db-deploy db-reset db-seed docker-dev

# -- Development --

dev:
	uv run uvicorn app.config.asgi:application --reload --host 0.0.0.0 --port 8000

start:
	uv run gunicorn app.config.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

build:
	docker build -f docker/Dockerfile -t django-template-monolith .

# -- Quality --

ruff-config:
	@printf 'extend = "%s"\n' "$$(uv run teo-ruff-config-path)" > ruff.extend.toml

lint: ruff-config
	uv run ruff check --fix .

lint-check: ruff-config
	uv run ruff check .

lint-types:
	uv run mypy .

format: ruff-config
	uv run ruff format .

format-check: ruff-config
	uv run ruff format --check .

test:
	uv run pytest

test-cov:
	uv run pytest --cov

check: lint-check format-check lint-types test

# -- Database --

db-migrate:
	uv run python manage.py makemigrations

db-deploy:
	uv run python manage.py migrate

db-reset:
	uv run python manage.py flush --no-input && uv run python manage.py migrate

db-seed:
	uv run python manage.py seed

# -- Docker --

docker-dev:
	docker compose up --build
