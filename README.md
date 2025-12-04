# RetailConnect Kenya

A Django REST API for connecting retailers and wholesalers in Kenya.

## 🚀 Quick Start Options

### Option 1: Docker (Recommended) 🐳

**Prerequisites:**
- Docker & Docker Compose installed

```bash
# 1. Clone and navigate to project
git clone <repository-url>
cd retailconnect_kenya

# 2. Copy environment file
cp .env.example .env

# 3. Build and run
docker-compose up --build

# 4. Access the application
# API Docs: http://localhost:8000/api/docs
# Admin: http://localhost:8000/admin (admin/admin123)
```

📖 **[Full Docker Setup Guide](./DOCKER_SETUP.md)**

### Option 2: Local Development 💻

**Prerequisites:**
- Python 3.11+ (virtualenv created at `.venv`)
- MySQL 8.x (or compatible)
- Redis (optional, for Celery broker/results)

```powershell
# Windows PowerShell

# 1) Activate virtual environment
.venv/Scripts/Activate.ps1

# 2) Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3) Create .env (see Environment Variables section)

# 4) Create database in MySQL
# Example: CREATE DATABASE retailconnect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 5) Apply migrations
python manage.py migrate

# 6) Create superuser
python manage.py createsuperuser

# 7) Run development server
python manage.py runserver
```

## Environment Variables (.env)

### For Docker:
```dotenv
# Core
SECRET_KEY=change-me
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Docker service names)
DB_NAME=retailconnect_db
DB_USER=retailuser
DB_PASSWORD=retailpassword
DB_HOST=db
DB_PORT=3306

# Redis (Docker service name)
REDIS_URL=redis://redis:6379/0
```

### For Local Development:
```dotenv
# Core
SECRET_KEY=change-me
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Local MySQL)
DB_NAME=retailconnect_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Redis (Local Redis)
REDIS_URL=redis://localhost:6379/0
```

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