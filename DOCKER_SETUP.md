# Docker Setup Guide for RetailConnect Kenya

This guide explains how to run the RetailConnect Kenya backend using Docker.

## 📋 Prerequisites

- Docker Desktop installed ([Download Docker](https://www.docker.com/products/docker-desktop))
- For WSL 2 Users: Enable WSL 2 integration in Docker Desktop settings
- Docker Compose installed (comes with Docker Desktop)
- Git (to clone the repository)

### ⚙️ WSL 2 Setup (Important!)

1. Open **Docker Desktop**
2. Go to **Settings** → **Resources** → **WSL Integration**
3. Enable "WSL integration" and select your WSL distro
4. Click **Apply & Restart**
5. Verify in WSL: `docker --version` and `docker compose version`

## 🚀 Quick Start (Development)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd retailconnect_kenya
```

### 2. Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

**Important:** The `.env.example` is already pre-configured for Docker. If running locally (not Docker):

```env
# For LOCAL DEVELOPMENT (not Docker)
DB_HOST=localhost
DB_NAME=retailconnect
DB_USER=root
DB_PASSWORD=
REDIS_URL=redis://localhost:6379/0
```

**For Docker:** `.env.example` already has correct values:

```env
# Core
SECRET_KEY=your-secret-key-here (keep the example one for dev)
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (Docker - matches docker-compose.yml)
DB_NAME=retailconnect_db
DB_USER=retailuser
DB_PASSWORD=retailpassword
DB_HOST=db
DB_PORT=3306

# Redis (Docker)
REDIS_URL=redis://redis:6379/0

# M-Pesa (Optional)
MPESA_CONSUMER_KEY=your-key
MPESA_CONSUMER_SECRET=your-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/v1/payments/mpesa/callback/
```

### 3. Build and Run Containers

**Option 1: From Windows PowerShell or CMD**
```bash
# Build the Docker images
docker compose build

# Start all services in background
docker compose up -d
```

**Option 2: From WSL 2 (after enabling WSL integration)**
```bash
# Build the Docker images
docker compose build

# Start all services in background
docker compose up -d
```

**View startup progress:**
```bash
docker compose logs -f
```

**Wait for all services to be healthy:**
```bash
docker compose ps
```

### 4. Access the Application

- **API Documentation**: http://localhost:8000/api/docs
- **Admin Panel**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/healthz

**Default Superuser:**
- Username: `admin`
- Password: `admin123`
- Email: `admin@retailconnect.com`

**⚠️ Change these credentials immediately in production!**

## 🛠️ Docker Commands

### View Running Containers

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs celery
docker-compose logs db

# Follow logs (live)
docker-compose logs -f web
```

### Stop Containers

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
```

### Execute Commands in Container

```bash
# Access Django shell
docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic

# Access container bash
docker-compose exec web bash
```

### Access Database

```bash
# MySQL shell
docker-compose exec db mysql -u retailuser -p retailconnect_db

# Or using root
docker-compose exec db mysql -u root -p
```

### Access Redis CLI

```bash
docker-compose exec redis redis-cli
```

## 📦 Services Overview

The Docker setup includes 5 services:

1. **db** - MySQL 8.0 database
   - Port: 3306
   - Data stored in `mysql_data` volume

2. **redis** - Redis 7 for Celery
   - Port: 6379
   - Data stored in `redis_data` volume

3. **web** - Django application
   - Port: 8000
   - Runs with Gunicorn (4 workers)

4. **celery** - Celery worker for background tasks
   - Processes async tasks
   - Handles M-Pesa callbacks, notifications, etc.

5. **celery-beat** - Celery scheduler
   - Runs scheduled/periodic tasks

## 🔧 Development Workflow

### Making Code Changes

When you edit code, the changes are automatically reflected (volume mounted). Just refresh your browser or restart the container if needed:

```bash
docker-compose restart web
```

### Adding New Dependencies

If you add packages to `requirements.txt`:

```bash
# Rebuild the image
docker-compose build web

# Restart the service
docker-compose up -d web
```

### Database Migrations

After changing models:

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

### Running Tests

```bash
docker-compose exec web python manage.py test
```

## 🚀 Production Deployment

For production, use the production docker-compose file:

### 1. Update Environment Variables

Create `.env` with production values:

```env
SECRET_KEY=generate-a-strong-secret-key
DEBUG=false
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=strong-database-password
# ... other production settings
```

### 2. Run Production Stack

```bash
docker-compose -f docker-compose.prod.yml up -d
```

This includes:
- Nginx reverse proxy
- Production-ready Gunicorn settings
- SSL/TLS support (configure nginx.conf)
- Database backups volume
- Logging

### 3. Setup SSL (Optional)

Place your SSL certificates in `./ssl/` directory:
- `ssl/certificate.crt`
- `ssl/private.key`

Update `nginx.conf` to enable HTTPS.

## 📊 Data Persistence

Data is stored in Docker volumes:

- `mysql_data` - Database files
- `redis_data` - Redis persistence
- `static_volume` - Static files (CSS, JS)
- `media_volume` - Uploaded files (images, etc.)

### Backup Database

```bash
# Create backup
docker-compose exec db mysqldump -u retailuser -p retailconnect_db > backup.sql

# Restore backup
docker-compose exec -T db mysql -u retailuser -p retailconnect_db < backup.sql
```

## 🐛 Troubleshooting

### Port Already in Use

If ports 8000, 3306, or 6379 are already in use:

1. Stop the conflicting service, or
2. Edit `docker-compose.yml` to use different ports:

```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Database Connection Issues

Check if MySQL is ready:

```bash
docker-compose logs db
```

Wait for: "mysqld: ready for connections"

### Container Crashes

View logs to diagnose:

```bash
docker-compose logs web
docker-compose logs celery
```

### Reset Everything

⚠️ **Warning: This deletes all data**

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up --build
```

### Permission Issues (Linux/Mac)

If you get permission errors:

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Or run with sudo
sudo docker-compose up
```

## 🔍 Health Checks

All services have health checks:

```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8000/healthz
```

## 📝 Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Django secret key | (required) |
| DEBUG | Debug mode | false |
| ALLOWED_HOSTS | Comma-separated hosts | localhost,127.0.0.1 |
| DB_NAME | Database name | retailconnect_db |
| DB_USER | Database user | retailuser |
| DB_PASSWORD | Database password | (required) |
| DB_HOST | Database host | db |
| DB_PORT | Database port | 3306 |
| REDIS_URL | Redis connection URL | redis://redis:6379/0 |
| MPESA_CONSUMER_KEY | M-Pesa API key | (optional) |
| MPESA_CONSUMER_SECRET | M-Pesa API secret | (optional) |

## 🎯 Next Steps

After setup:

1. ✅ Access admin panel and change default password
2. ✅ Configure M-Pesa credentials (if using payments)
3. ✅ Test API endpoints at `/api/docs`
4. ✅ Create test users (retailers, wholesalers)
5. ✅ Add product categories and products
6. ✅ Test complete order flow

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Docker Best Practices](https://docs.docker.com/samples/django/)
- [Main README](./README.md)
- [Architecture Guide](./ARCHITECTURE.md)

## 💡 Tips

- Use `docker-compose logs -f` to follow logs in real-time
- Keep `.env` file secure and never commit it to Git
- Use `docker-compose down` before `docker-compose up` when changing compose files
- Monitor container resource usage with `docker stats`
- Use production compose file for staging/production environments

---

**Happy Coding! 🚀**
