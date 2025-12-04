# Deployment Guide - RetailConnect Kenya

This guide covers deploying RetailConnect Kenya to various platforms using Docker.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [AWS Deployment](#aws-deployment)
- [DigitalOcean Deployment](#digitalocean-deployment)
- [Heroku Deployment](#heroku-deployment)
- [Google Cloud Platform](#google-cloud-platform)
- [Self-Hosted Server](#self-hosted-server)
- [Post-Deployment](#post-deployment)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Docker and Docker Compose installed on target server
- ✅ Domain name (optional but recommended)
- ✅ SSL certificate (Let's Encrypt is free)
- ✅ Production environment variables ready
- ✅ M-Pesa API credentials (if using payments)
- ✅ Database backup strategy

---

## AWS Deployment

### Using EC2 + RDS

#### 1. Launch EC2 Instance

```bash
# Choose Ubuntu 22.04 LTS
# Instance type: t3.medium or higher
# Configure security groups:
#   - Port 80 (HTTP)
#   - Port 443 (HTTPS)
#   - Port 22 (SSH - your IP only)
```

#### 2. Install Docker on EC2

```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 3. Setup RDS Database (Optional)

```bash
# Create RDS MySQL instance
# - Engine: MySQL 8.0
# - Instance class: db.t3.micro (for testing)
# - Storage: 20GB minimum
# - Enable automatic backups

# Update .env with RDS endpoint
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_NAME=retailconnect_db
DB_USER=admin
DB_PASSWORD=your-strong-password
```

#### 4. Deploy Application

```bash
# Clone repository
git clone https://github.com/your-username/retailconnect.git
cd retailconnect

# Create production .env
nano .env
# (Add all production variables)

# Deploy with production compose
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### 5. Setup Nginx & SSL

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certificate auto-renewal is configured automatically
```

---

## DigitalOcean Deployment

### Using Droplet + Managed Database

#### 1. Create Droplet

```bash
# Create Ubuntu 22.04 droplet
# Size: 2GB RAM minimum
# Add SSH key
# Enable monitoring
```

#### 2. Create Managed MySQL Database

```bash
# From DigitalOcean dashboard:
# - Create MySQL 8 database
# - Note connection details
# - Add droplet to trusted sources
```

#### 3. Setup Application

```bash
# SSH into droplet
ssh root@your-droplet-ip

# Install Docker (same as AWS)
curl -fsSL https://get.docker.com | sh
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone https://github.com/your-username/retailconnect.git
cd retailconnect

# Create .env with DO database credentials
cat > .env << EOF
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=false
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_HOST=your-do-database-host
DB_PORT=25060
DB_NAME=retailconnect_db
DB_USER=doadmin
DB_PASSWORD=your-db-password
REDIS_URL=redis://redis:6379/0
EOF

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

#### 4. Configure Domain

```bash
# Point your domain A records to droplet IP
# @ → droplet-ip
# www → droplet-ip

# Setup SSL
apt-get install certbot python3-certbot-nginx -y
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Heroku Deployment

Heroku doesn't support docker-compose directly, but you can deploy using container registry.

#### 1. Install Heroku CLI

```bash
# Windows
choco install heroku-cli

# Mac
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2. Prepare for Heroku

Create `heroku.yml`:

```yaml
build:
  docker:
    web: Dockerfile
run:
  web: gunicorn retailconnect.wsgi:application --bind 0.0.0.0:$PORT
```

#### 3. Deploy

```bash
# Login to Heroku
heroku login
heroku container:login

# Create app
heroku create your-app-name

# Add MySQL addon
heroku addons:create jawsdb:kitefin

# Add Redis addon
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=$(openssl rand -base64 32)
heroku config:set DEBUG=false
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

---

## Google Cloud Platform

### Using Cloud Run + Cloud SQL

#### 1. Setup GCP Project

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Initialize
gcloud init

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable compute.googleapis.com
```

#### 2. Create Cloud SQL Instance

```bash
# Create MySQL instance
gcloud sql instances create retailconnect-db \
  --database-version=MYSQL_8_0 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create retailconnect_db --instance=retailconnect-db

# Create user
gcloud sql users create retailuser \
  --instance=retailconnect-db \
  --password=your-strong-password
```

#### 3. Build and Deploy

```bash
# Build image
gcloud builds submit --tag gcr.io/your-project-id/retailconnect

# Deploy to Cloud Run
gcloud run deploy retailconnect \
  --image gcr.io/your-project-id/retailconnect \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --add-cloudsql-instances your-project-id:us-central1:retailconnect-db \
  --set-env-vars "DB_HOST=/cloudsql/your-project-id:us-central1:retailconnect-db"
```

---

## Self-Hosted Server

### Using Your Own Server (VPS)

#### 1. Server Requirements

- **OS:** Ubuntu 22.04 LTS or Debian 11
- **RAM:** 2GB minimum, 4GB recommended
- **CPU:** 2 cores minimum
- **Storage:** 20GB minimum
- **Network:** 100Mbps connection

#### 2. Initial Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install essential packages
sudo apt-get install -y git curl wget vim ufw fail2ban

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com | sudo sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. Deploy Application

```bash
# Create application directory
sudo mkdir -p /opt/retailconnect
sudo chown $USER:$USER /opt/retailconnect
cd /opt/retailconnect

# Clone repository
git clone https://github.com/your-username/retailconnect.git .

# Create production .env
cat > .env << EOF
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=false
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=retailconnect_db
DB_USER=retailuser
DB_PASSWORD=$(openssl rand -base64 32)
DB_HOST=db
DB_PORT=3306
REDIS_URL=redis://redis:6379/0
MPESA_CONSUMER_KEY=your-key
MPESA_CONSUMER_SECRET=your-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/v1/payments/mpesa/callback/
EOF

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

#### 4. Setup Auto-Start

Create systemd service:

```bash
sudo nano /etc/systemd/system/retailconnect.service
```

Add:

```ini
[Unit]
Description=RetailConnect Kenya
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/retailconnect
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable retailconnect
sudo systemctl start retailconnect
```

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Check all containers are running
docker-compose ps

# Test health endpoint
curl https://yourdomain.com/healthz

# Check API docs
curl https://yourdomain.com/api/docs
```

### 2. Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### 3. Setup Monitoring

```bash
# Install monitoring tools
docker run -d --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower
```

### 4. Configure Backups

```bash
# Create backup script
cat > /opt/retailconnect/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/retailconnect/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T db mysqldump -u retailuser -p$DB_PASSWORD retailconnect_db > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz media/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
EOF

chmod +x /opt/retailconnect/backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/retailconnect/backup.sh") | crontab -
```

### 5. Setup Logging

```bash
# Configure log rotation
sudo nano /etc/logrotate.d/retailconnect
```

Add:

```
/opt/retailconnect/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
}
```

### 6. Security Checklist

- [ ] Change default superuser password
- [ ] Enable HTTPS (SSL certificate)
- [ ] Configure firewall (ufw/iptables)
- [ ] Setup fail2ban for SSH
- [ ] Regular security updates
- [ ] Strong database passwords
- [ ] Secure M-Pesa credentials
- [ ] Enable two-factor authentication for admin
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity

### 7. Performance Tuning

```bash
# Scale Celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery=4

# Increase Gunicorn workers (edit docker-compose.prod.yml)
command: gunicorn retailconnect.wsgi:application --bind 0.0.0.0:8000 --workers 8

# Enable caching (add to settings.py)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
    }
}
```

### 8. Monitoring & Alerts

```bash
# Setup Sentry for error tracking (add to requirements.txt)
sentry-sdk>=1.40.0

# Configure in settings.py
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check specific service
docker-compose -f docker-compose.prod.yml logs web
```

### Database Connection Failed

```bash
# Test database connection
docker-compose exec web python manage.py dbshell

# Check database container
docker-compose exec db mysql -u retailuser -p
```

### SSL Certificate Issues

```bash
# Renew certificate manually
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

---

## Useful Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update application
git pull
docker-compose -f docker-compose.prod.yml up -d --build

# Backup database
docker-compose exec db mysqldump -u retailuser -p retailconnect_db > backup.sql

# Restore database
docker-compose exec -T db mysql -u retailuser -p retailconnect_db < backup.sql
```

---

## Support

For issues or questions:
- 📖 [Main README](./README.md)
- 🐳 [Docker Setup Guide](./DOCKER_SETUP.md)
- 📋 [Docker Commands](./DOCKER_COMMANDS.md)
- 🏗️ [Architecture Guide](./ARCHITECTURE.md)

---

**🚀 Happy Deploying!**
