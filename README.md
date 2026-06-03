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
- Docker and Docker Compose
- PostgreSQL
- Redis

---

## Quick Start

```bash
uv sync
cp .env.example .env
cp .env.test.example .env.test
docker compose up -d db redis
uv run python manage.py migrate
make dev
```

API docs are reachable at `http://localhost:8000/docs`.

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
| `make django-check-deploy` | Run Django deployment checks with production security defaults |
| `make lint`        | Lint and fix with Ruff                   |
| `make lint-types`  | Type check with mypy                     |
| `make format`      | Format with Ruff                         |
| `make db-migrate`  | Generate new migration                   |
| `make db-deploy`   | Apply all migrations                     |
| `make db-reset`    | Flush and re-migrate                     |
| `make db-seed`     | Seed deterministic sample data           |
| `make docker-dev`  | Start full stack via Docker Compose      |

---

## Migration Safety

Run Django migrations as a pre-deploy step with `make db-deploy` before the new
application version starts. Do not run migrations from application startup,
request handlers, seed scripts, or tests that point at a shared database.

Production migrations must be backward-compatible with the currently running
version. Use expand-contract changes: add nullable columns, new tables, and new
indexes before code depends on them; backfill explicitly when needed; deploy code
that stops reading the old shape; then remove or narrow schema in a later
release.

`make db-deploy` is safe to re-run when there are no pending migrations.
Production rollback is a database backup restore plus compatible code, or a
forward-fix migration. Django's targeted migrate commands may be useful locally,
but this template does not treat down migrations as the primary production
rollback strategy. `make db-reset` is local/test-only.

Avoid destructive one-step migrations, renaming columns without a compatibility
window, adding non-null columns without defaults/backfills, and combining schema
contraction with the first code release that stops using the old shape.

---

## Health and Observability

| Endpoint            | Description                                          |
| ------------------- | ---------------------------------------------------- |
| `GET /health/live`  | Liveness probe                                       |
| `GET /health/ready` | Readiness probe (checks PostgreSQL + Redis)          |
| `GET /health`       | Full health summary with dependency and runtime info |
| `GET /metrics`      | Prometheus metrics endpoint                          |

Structured JSON logs are emitted via `structlog`, with request ID propagation
through the shared middleware stack.

---

## Environment Variables

| Variable         | Description                  | Default                  |
| ---------------- | ---------------------------- | ------------------------ |
| `DEBUG`          | Django debug mode            | `true`                   |
| `PORT`           | Application port             | `8000`                   |
| `HTTP_PORT`      | Nginx host port in production compose | `8080` |
| `DATABASE_URL`   | PostgreSQL connection string | Required                 |
| `REDIS_HOST`     | Redis host                   | `localhost`              |
| `REDIS_PORT`     | Redis port                   | `6379`                   |
| `API_PREFIX`     | Versioned API route prefix   | `/api/v1`                |
| `CORS_ORIGINS`   | Allowed frontend origins     | `http://localhost:3000`  |
| `LOG_LEVEL`      | Logging verbosity            | `INFO`                   |
| `METRICS_ENABLED`| Enable Prometheus metrics    | `true`                   |
| `SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS in deployment | `false` |
| `SECURE_HSTS_SECONDS` | HSTS max age in deployment | `0` |
| `SESSION_COOKIE_SECURE` | Require HTTPS for session cookies | `false` |
| `CSRF_COOKIE_SECURE` | Require HTTPS for CSRF cookies | `false` |

See `.env.example` and `.env.test.example` for the full set.

### Environment Promotion

Use `.env.example` as the complete variable inventory, then review values before
promoting beyond local development:

- Keep `DEBUG=false`, `LOG_LEVEL=info`, and `LOG_JSON=true`.
- Replace `SECRET_KEY`, local Postgres, Redis, and pgAdmin defaults; pgAdmin is
  local-only.
- Set `ALLOWED_HOSTS` and `CORS_ORIGIN` to deployed hosts/origins. Do not use
  wildcards.
- Enable HTTPS-owned settings when TLS is active:
  `SECURE_SSL_REDIRECT=true`, `SECURE_HSTS_SECONDS=31536000`,
  `SESSION_COOKIE_SECURE=true`, and `CSRF_COOKIE_SECURE=true`.
- Run `make django-check-deploy` before promoting a production configuration.
- Production schema changes go through `make db-deploy`.
- Use `docker-compose.prod.yml` for a production-like local smoke test:
  `docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build`.
  Nginx is the public entry point on `HTTP_PORT`; the app, Postgres, and Redis
  ports are internal to the Compose network.

---

## Project Structure

| Path                 | Purpose                                                       |
| -------------------- | ------------------------------------------------------------- |
| `app/config/`        | Django settings, URLs, ASGI/WSGI bootstrap                    |
| `app/modules/tasks/` | Sample tasks domain with model, schema, service, and router   |
| `app/shared/`        | Shared DB, Redis, health, metrics, middleware, and logging    |
| `app/main.py`        | Django Ninja API instance                                     |
| `manage.py`          | Django management CLI                                         |
| `tests/`             | pytest suite                                                  |
| `docker/`            | Development and production container files                    |

---

## Shared Governance

| Area           | Tooling                                        |
| -------------- | ---------------------------------------------- |
| Dependency updates | Renovate                                   |
| Issue intake   | GitHub issue templates                         |
| Change review  | Pull request template                          |
| CI             | GitHub Actions for lint, format, types, tests |
| Security       | Trivy, dependency review, `pip-audit`          |

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
