# Architecture Overview

This document outlines patterns and practices to keep the RetailConnect backend scalable, maintainable, and production-ready.

## Layering and Boundaries
- **Apps by domain**: `apps/users`, `apps/products`, `apps/orders`, `apps/payments`, `apps/delivery`, `apps/notifications`, `apps/analytics`.
- **Thin views**: Prefer DRF viewsets/APIViews with minimal logic.
- **Services**: Business logic in `apps/<domain>/services.py` (pure functions/classes). Views call services.
- **Repositories**: Complex ORM/data access isolated in `apps/<domain>/repositories.py` if needed.
- **Serializers/DTOs**: Keep validation and IO mapping distinct from domain logic.

## Settings Strategy
- Split settings into modules under `retailconnect/settings/`:
  - `base.py`: shared defaults
  - `dev.py`: debug, local DB, CORS relaxed
  - `prod.py`: secure defaults, allowed hosts, robust logging
  - `test.py`: fast password hashers, in-memory DB optional
- Select via `DJANGO_SETTINGS_MODULE=retailconnect.settings.dev|prod|test`.

## API Versioning
- Prefix routes with `/api/v1/...` and plan `/api/v2` when breaking changes arise.
- Use `drf-spectacular` to keep schema stable and documented.

## Authentication & Authorization
- **JWT** via `rest_framework_simplejwt` (already wired).
- Consider **token blacklist** on logout.
- Use per-view **permissions** (e.g., `IsAuthenticated`, `IsAdminUser`, custom role permissions).

## Async & Background Processing
- **Celery** for async tasks: MPesa callbacks processing, notifications, analytics rolls.
- Define queues: `default`, `payments`, `notifications`.
- Add idempotency keys for payment workflows and retry policies with backoff.

## Files & Media
- Static via `whitenoise` in dev; use S3-compatible storage (e.g., `django-storages`) in prod.

## Observability
- **Logging**: structured JSON logs in prod; request IDs.
- **Health checks**: `/healthz` endpoint (DB + cache probes).
- **Metrics**: Prometheus or StatsD for request latency, Celery worker stats.
- **Error tracking**: Sentry integration.

## Security
- Set `DEBUG=false` in prod; strong `SECRET_KEY`.
- Restrict `ALLOWED_HOSTS`.
- CORS whitelist only trusted origins.
- Validate/escape user input; throttle auth endpoints.

## Database & Migrations
- Use **atomic transactions** for multi-step writes.
- Avoid N+1 via `.select_related/.prefetch_related`.
- Use DB indexes for frequent filters/search.

## Testing Strategy
- Unit tests for services and serializers.
- API tests for critical flows (auth, orders, payments).
- Use factories (factory_boy) and `pytest` for speed.

## Deployment
- Containerize with Docker; use Gunicorn+Uvicorn workers for ASGI.
- Apply migrations on deploy; run `collectstatic`.
- Configure Celery workers and beat for periodic tasks.

## Directory Conventions (example)
```
apps/
  products/
    services.py
    repositories.py
    tests/
retailconnect/
  settings/
    base.py
    dev.py
    prod.py
    test.py
```

## Immediate Next Steps
- Create settings split and `/api/v1` routing.
- Introduce `services.py` files per domain and move business logic.
- Add `/healthz` and basic logging configuration.
