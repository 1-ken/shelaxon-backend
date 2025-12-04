# Docker Quick Reference - RetailConnect Kenya

## 🚀 Getting Started

```bash
# Start all services (first time)
docker-compose up --build

# Start all services (background)
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

## 📊 Monitoring

```bash
# View running containers
docker-compose ps

# View all logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs celery
docker-compose logs db

# Follow logs (live)
docker-compose logs -f web

# View last 100 lines
docker-compose logs --tail=100 web
```

## 🔧 Django Commands

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create migrations
docker-compose exec web python manage.py makemigrations

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Django shell
docker-compose exec web python manage.py shell

# Collect static files
docker-compose exec web python manage.py collectstatic

# Run tests
docker-compose exec web python manage.py test
```

## 💾 Database Commands

```bash
# Access MySQL shell
docker-compose exec db mysql -u retailuser -p retailconnect_db

# Backup database
docker-compose exec db mysqldump -u retailuser -p retailconnect_db > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db mysql -u retailuser -p retailconnect_db < backup.sql

# View database logs
docker-compose logs db
```

## 🔄 Service Management

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart web
docker-compose restart celery

# Rebuild and restart
docker-compose up -d --build web

# Scale workers (run 3 celery workers)
docker-compose up -d --scale celery=3
```

## 🐚 Container Access

```bash
# Access web container bash
docker-compose exec web bash

# Access db container bash
docker-compose exec db bash

# Access redis CLI
docker-compose exec redis redis-cli

# Run command without entering container
docker-compose exec web ls -la
```

## 📦 Images & Cleanup

```bash
# View images
docker images

# Remove unused images
docker image prune

# Remove all stopped containers
docker container prune

# Remove unused volumes
docker volume prune

# Remove everything (⚠️ nuclear option)
docker system prune -a --volumes
```

## 🔍 Debugging

```bash
# Check service health
docker-compose ps

# Inspect container
docker inspect retailconnect_web

# View container resource usage
docker stats

# View container processes
docker-compose top

# View service configuration
docker-compose config
```

## 🔐 Production Commands

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production services
docker-compose -f docker-compose.prod.yml down
```

## 🆘 Troubleshooting

```bash
# Container won't start - check logs
docker-compose logs <service-name>

# Port already in use - stop service using port
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Database connection failed - wait for MySQL
docker-compose logs db | grep "ready for connections"

# Reset everything
docker-compose down -v
docker-compose up --build

# Clear Docker cache
docker builder prune -a
```

## 📝 Environment Variables

```bash
# View environment variables in container
docker-compose exec web env

# Check specific variable
docker-compose exec web printenv DB_HOST
```

## 🔄 Updates & Rebuilds

```bash
# Update code and rebuild
git pull
docker-compose build
docker-compose up -d

# Update specific service
docker-compose build web
docker-compose up -d web

# Force recreate containers
docker-compose up -d --force-recreate
```

## 💡 Useful Combinations

```bash
# Stop, rebuild, and start
docker-compose down && docker-compose up --build

# Fresh start (delete all data)
docker-compose down -v && docker-compose up --build

# Quick restart after code changes
docker-compose restart web

# View logs while starting
docker-compose up --build | tee docker-logs.txt
```

## 🎯 Common Workflows

### Adding New Python Package
```bash
# 1. Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# 2. Rebuild web service
docker-compose build web

# 3. Restart web service
docker-compose up -d web
```

### Database Migration
```bash
# 1. Make model changes in code
# 2. Create migrations
docker-compose exec web python manage.py makemigrations

# 3. Apply migrations
docker-compose exec web python manage.py migrate

# 4. Restart web (optional)
docker-compose restart web
```

### Backup Before Update
```bash
# 1. Backup database
docker-compose exec db mysqldump -u retailuser -p retailconnect_db > backup.sql

# 2. Pull latest code
git pull

# 3. Rebuild and restart
docker-compose up -d --build

# 4. Run migrations if needed
docker-compose exec web python manage.py migrate
```

## 📞 Quick Help

```bash
# View compose file help
docker-compose --help

# View specific command help
docker-compose up --help
docker-compose logs --help

# View Docker help
docker --help
```

---

**💡 Tip:** Add these as aliases in your shell for quick access!

**🔗 Full Guide:** See [DOCKER_SETUP.md](./DOCKER_SETUP.md) for detailed documentation.
