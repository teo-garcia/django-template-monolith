<div align="center">

# Django Template Monolith

**Production-ready Django starter with Django Ninja, PostgreSQL, Redis, and
modern Python tooling**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://djangoproject.com)
[![Django Ninja](https://img.shields.io/badge/Django_Ninja-1.4-009688)](https://django-ninja.dev)

Part of the [@teo-garcia/templates](https://github.com/teo-garcia/templates)
ecosystem

</div>

---

## Features

| Category          | Technologies                                          |
| ----------------- | ----------------------------------------------------- |
| **Framework**     | Django 5.2 with ASGI (Uvicorn/Gunicorn)               |
| **API**           | Django Ninja (automatic OpenAPI, Pydantic schemas)     |
| **Database**      | PostgreSQL 17, Django ORM, native migrations           |
| **Cache**         | Redis with django-redis                                |
| **Type Safety**   | mypy strict mode with django-stubs                     |
| **Testing**       | pytest-django, pytest-cov                              |
| **Code Quality**  | Ruff (lint + format), pre-commit, commitizen           |
| **Observability** | structlog (JSON), Prometheus metrics, request ID       |
| **Security**      | Security headers, rate limiting, CORS                  |
| **Infra**         | Docker (multi-stage), Compose, Renovate                |

---

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management

---

## Quick Start

```bash
uv sync
cp .env.example .env
uv run python manage.py migrate
make dev
```

API docs at `http://localhost:8000/api/docs`.

---

## Scripts (Makefile)

| Command            | Description                              |
| ------------------ | ---------------------------------------- |
| `make dev`         | Start dev server with hot reload         |
| `make start`       | Run production server (Gunicorn)         |
| `make build`       | Build production Docker image            |
| `make test`        | Run tests                                |
| `make test-cov`    | Run tests with coverage                  |
| `make check`       | Run lint, format, typecheck, and tests   |
| `make lint`        | Lint and fix with Ruff                   |
| `make lint-types`  | Type check with mypy                     |
| `make format`      | Format with Ruff                         |
| `make db-migrate`  | Generate new migration                   |
| `make db-deploy`   | Apply all migrations                     |
| `make db-reset`    | Flush and re-migrate                     |
| `make docker-dev`  | Start full stack via Docker Compose      |

---

## Project Structure

| Path                   | Purpose                               |
| ---------------------- | ------------------------------------- |
| `app/config/`          | Django settings, URLs, ASGI/WSGI      |
| `app/modules/tasks/`   | Tasks domain (model, schema, service, router) |
| `app/shared/`          | Cross-cutting infra (DB, Redis, middleware, health, metrics, logging, exceptions) |
| `app/main.py`          | Django Ninja API instance              |
| `manage.py`            | Django management CLI                  |
| `tests/`               | pytest test suite                      |
| `docker/`              | Dockerfiles (prod + dev)               |

---

## Related Templates

| Template                       | Description             |
| ------------------------------ | ----------------------- |
| `fastapi-template-monolith`    | FastAPI backend          |
| `nest-template-monolith`       | NestJS backend           |
| `react-template-next`          | Next.js frontend         |
| `react-template-rr`            | React Router frontend    |
| `react-template-tanstack-start`| TanStack Start frontend  |

---

## License

MIT

---

<div align="center">
  <sub>Built by <a href="https://github.com/teo-garcia">teo-garcia</a></sub>
</div>
