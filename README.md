# RetailConnect Kenya

A Django REST API for connecting retailers and wholesalers in Kenya.

## Prerequisites
- Python 3.14 (virtualenv created at `.venv`)
- MySQL 8.x (or compatible)
- Redis (optional, for Celery broker/results)

## Quick Start (Windows PowerShell)

```powershell
# 1) Activate virtual environment
C:/Users/kenni/Desktop/retailconnect_kenya/rr/retailconnect_kenya/.venv/Scripts/Activate.ps1

# 2) Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3) Create .env with your settings (see below)
# 4) Create database in MySQL
#    Example: CREATE DATABASE retailconnect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 5) Apply migrations
python manage.py migrate

# 6) Create superuser (optional)
python manage.py createsuperuser

# 7) Run development server
python manage.py runserver
```

## Environment Variables (.env)
Create a `.env` file in the project root (`retailconnect_kenya`) with values matching your setup.

```dotenv
# Core
SECRET_KEY=change-me
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=retailconnect_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Redis / Celery (optional)
REDIS_URL=redis://localhost:6379/0

# M-Pesa (fill with real credentials)
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_SHORTCODE=
MPESA_PASSKEY=
MPESA_CALLBACK_URL=
```

## Project Structure
- `manage.py`: Django management entrypoint
- `retailconnect/settings.py`: Main Django settings
- `retailconnect/urls.py`: Root URL router
- `apps/*`: Feature apps (users, products, orders, payments, delivery, notifications, analytics)
- `utils/mpesa.py`: M-Pesa integration helpers

## API Docs
- OpenAPI schema via `drf-spectacular`.
- Add to `retailconnect/urls.py` if not present:

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.urls import path

urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
```

Visit `http://127.0.0.1:8000/api/docs/` after starting the server.

## Common Tasks
- Run tests: `python manage.py test`
- Create app: `python manage.py startapp apps.example`
- Collect static (production): `python manage.py collectstatic`

## Troubleshooting
- MySQL client not found: install MySQL Connector/C or `mysqlclient` build tools.
- Migration errors: verify DB credentials and that the database exists.
- Import errors: ensure virtualenv is activated and dependencies installed.

## Production Notes
- Set `DEBUG=false` and use a strong `SECRET_KEY`.
- Configure `ALLOWED_HOSTS` for your domain/IP.
- Use a proper WSGI/ASGI server (gunicorn/uvicorn) behind Nginx/Apache.
- Set up environment variables in your deployment platform.