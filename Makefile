.PHONY: help build up down restart logs shell test migrate createsuperuser backup restore clean

# Default target
help:
	@echo "RetailConnect Kenya - Docker Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs (all services)"
	@echo "  make logs-web       - View web service logs"
	@echo "  make logs-celery    - View celery logs"
	@echo "  make shell          - Access Django shell"
	@echo "  make bash           - Access web container bash"
	@echo "  make test           - Run tests"
	@echo "  make migrate        - Run database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make createsuperuser - Create Django superuser"
	@echo "  make collectstatic  - Collect static files"
	@echo "  make backup         - Backup database"
	@echo "  make restore        - Restore database from backup"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make rebuild        - Clean build and start"
	@echo "  make prod-up        - Start production services"
	@echo "  make prod-down      - Stop production services"

# Build images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Start with logs
up-logs:
	docker-compose up

# Stop services
down:
	docker-compose down

# Restart services
restart:
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

logs-web:
	docker-compose logs -f web

logs-celery:
	docker-compose logs -f celery

logs-db:
	docker-compose logs -f db

# Django shell
shell:
	docker-compose exec web python manage.py shell

# Container bash
bash:
	docker-compose exec web bash

# Run tests
test:
	docker-compose exec web python manage.py test

# Database migrations
migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

# Create superuser
createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# Collect static files
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

# Database backup
backup:
	docker-compose exec db mysqldump -u retailuser -pretailpassword retailconnect_db > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup created: backup_$$(date +%Y%m%d_%H%M%S).sql"

# Database restore (use: make restore FILE=backup.sql)
restore:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify FILE=backup.sql"; \
		exit 1; \
	fi
	docker-compose exec -T db mysql -u retailuser -pretailpassword retailconnect_db < $(FILE)
	@echo "Database restored from $(FILE)"

# Clean everything
clean:
	docker-compose down -v
	docker system prune -f

# Rebuild everything
rebuild: clean build up

# Production
prod-up:
	docker-compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

# Status
ps:
	docker-compose ps

# Quick restart web service
restart-web:
	docker-compose restart web

# View web container resource usage
stats:
	docker stats retailconnect_web retailconnect_celery retailconnect_db retailconnect_redis
