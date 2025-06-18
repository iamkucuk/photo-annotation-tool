# Deployment Guide

This guide covers various deployment options for the Photo Annotation Tool, from local development to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Environment Configuration](#environment-configuration)
- [Security Considerations](#security-considerations)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **Python**: 3.11 or higher
- **Memory**: Minimum 512MB RAM, Recommended 2GB+
- **Storage**: Minimum 1GB free space (more for image storage)
- **Network**: HTTP/HTTPS access for web interface

### Dependencies

- **uv** (recommended) or **pip** for package management
- **Python development headers** for PIL/Pillow compilation
- **Web server** (nginx, Apache) for production deployment
- **Process manager** (systemd, supervisord) for production

## Local Development

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd photo-annotation-tool

# Install dependencies
uv sync --dev

# Run development server
uv run uvicorn src.photo_annotator.main:app --reload --port 8001
```

### Development Configuration

The application runs with default settings suitable for development:

- **Host**: `127.0.0.1` (localhost only)
- **Port**: `8001`
- **Debug**: Enabled (auto-reload on code changes)
- **CORS**: Permissive (allows all origins)
- **Uploads**: `./uploads/` directory
- **CSV**: `./annotations.csv` file

### Development Environment Variables

```bash
# Optional development overrides
export DEVELOPMENT=true
export LOG_LEVEL=debug
export UPLOAD_DIR=/custom/upload/path
export CSV_FILE=/custom/annotations.csv
```

## Production Deployment

### Manual Production Setup

#### 1. System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+ (Ubuntu 22.04+)
sudo apt install python3.11 python3.11-dev python3.11-venv

# Install system dependencies
sudo apt install build-essential libjpeg-dev zlib1g-dev libpng-dev
```

#### 2. Application Setup

```bash
# Create application user
sudo useradd -r -s /bin/false photo-annotator

# Create application directory
sudo mkdir -p /opt/photo-annotator
sudo chown photo-annotator:photo-annotator /opt/photo-annotator

# Switch to application user
sudo -u photo-annotator -i

# Navigate to application directory
cd /opt/photo-annotator

# Clone and setup application
git clone <repository-url> app
cd app

# Install dependencies (production only)
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e .

# Create necessary directories
mkdir -p uploads/thumbnails
mkdir -p data
mkdir -p logs
```

#### 3. Production Configuration

Create production configuration file:

```bash
# /opt/photo-annotator/app/.env
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
UPLOAD_DIR=/opt/photo-annotator/app/uploads
CSV_FILE=/opt/photo-annotator/app/data/annotations.csv
MAX_FILE_SIZE=10485760
ALLOWED_ORIGINS=https://yourdomain.com
```

#### 4. Systemd Service

Create systemd service file:

```ini
# /etc/systemd/system/photo-annotator.service
[Unit]
Description=Photo Annotation Tool
After=network.target

[Service]
Type=exec
User=photo-annotator
Group=photo-annotator
WorkingDirectory=/opt/photo-annotator/app
Environment=PATH=/opt/photo-annotator/app/venv/bin
EnvironmentFile=/opt/photo-annotator/app/.env
ExecStart=/opt/photo-annotator/app/venv/bin/uvicorn src.photo_annotator.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable photo-annotator
sudo systemctl start photo-annotator
sudo systemctl status photo-annotator
```

#### 5. Nginx Reverse Proxy

Install and configure nginx:

```bash
sudo apt install nginx

# Create nginx configuration
sudo tee /etc/nginx/sites-available/photo-annotator <<EOF
server {
    listen 80;
    server_name yourdomain.com;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /uploads/ {
        alias /opt/photo-annotator/app/uploads/;
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/photo-annotator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. SSL Configuration (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### Production Monitoring

#### Health Check Endpoint

The application provides a health check endpoint at `/health`:

```bash
curl -f http://localhost:8000/health || exit 1
```

#### Log Management

Configure log rotation:

```bash
# /etc/logrotate.d/photo-annotator
/opt/photo-annotator/app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

## Docker Deployment

### Dockerfile

Create a Dockerfile for containerized deployment:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -r -s /bin/false -u 1000 photo-annotator

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/

# Create necessary directories
RUN mkdir -p uploads/thumbnails data logs

# Change ownership
RUN chown -R photo-annotator:photo-annotator /app

# Switch to non-root user
USER photo-annotator

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "src.photo_annotator.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

For development and simple production deployments:

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - uploads:/app/uploads
      - data:/app/data
      - logs:/app/logs
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=info
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - uploads:/var/www/uploads:ro
      - certbot-data:/etc/letsencrypt
    depends_on:
      - app
    restart: unless-stopped

  certbot:
    image: certbot/certbot
    volumes:
      - certbot-data:/etc/letsencrypt
      - certbot-challenges:/var/www/certbot
    command: certonly --webroot --webroot-path=/var/www/certbot --email your-email@domain.com --agree-tos --no-eff-email -d yourdomain.com

volumes:
  uploads:
  data:
  logs:
  certbot-data:
  certbot-challenges:
```

### Docker Commands

```bash
# Build image
docker build -t photo-annotator .

# Run container
docker run -d \
  --name photo-annotator \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/data:/app/data \
  photo-annotator

# Using docker-compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Scale application
docker-compose up -d --scale app=3
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS

1. **Build and push Docker image to ECR**:

```bash
# Create ECR repository
aws ecr create-repository --repository-name photo-annotator

# Get login token
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com

# Build and tag image
docker build -t photo-annotator .
docker tag photo-annotator:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/photo-annotator:latest

# Push image
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/photo-annotator:latest
```

2. **Create ECS task definition**:

```json
{
  "family": "photo-annotator",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "photo-annotator",
      "image": "<account-id>.dkr.ecr.us-west-2.amazonaws.com/photo-annotator:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/photo-annotator",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "mountPoints": [
        {
          "sourceVolume": "uploads",
          "containerPath": "/app/uploads"
        }
      ]
    }
  ],
  "volumes": [
    {
      "name": "uploads",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-xxxxxxxx"
      }
    }
  ]
}
```

#### Using AWS App Runner

```yaml
# apprunner.yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install --upgrade pip
      - pip install -e .
run:
  runtime-version: 3.11
  command: uvicorn src.photo_annotator.main:app --host 0.0.0.0 --port 8000
  network:
    port: 8000
  env:
    - name: ENVIRONMENT
      value: production
```

### Google Cloud Platform (GCP)

#### Using Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/photo-annotator', '.']
images:
  - 'gcr.io/$PROJECT_ID/photo-annotator'
```

Deploy to Cloud Run:

```bash
# Build and deploy
gcloud builds submit --config cloudbuild.yaml

# Deploy to Cloud Run
gcloud run deploy photo-annotator \
  --image gcr.io/$PROJECT_ID/photo-annotator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name photo-annotator-rg --location eastus

# Create container instance
az container create \
  --resource-group photo-annotator-rg \
  --name photo-annotator \
  --image photo-annotator:latest \
  --cpu 1 \
  --memory 1 \
  --ports 8000 \
  --environment-variables ENVIRONMENT=production \
  --restart-policy Always
```

## Environment Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Deployment environment |
| `HOST` | `127.0.0.1` | Server bind address |
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `info` | Logging level |
| `UPLOAD_DIR` | `uploads` | Upload directory path |
| `CSV_FILE` | `annotations.csv` | CSV file path |
| `MAX_FILE_SIZE` | `10485760` | Max file size in bytes |
| `ALLOWED_ORIGINS` | `["*"]` | CORS allowed origins |

### Configuration Files

#### Production Configuration

```python
# config/production.py
import os

class ProductionConfig:
    DEBUG = False
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8000))
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
    CSV_FILE = os.getenv("CSV_FILE", "/app/data/annotations.csv")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
```

#### Environment-specific Settings

```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
UPLOAD_DIR=/app/uploads
CSV_FILE=/app/data/annotations.csv
ALLOWED_ORIGINS=https://yourdomain.com

# .env.staging
ENVIRONMENT=staging
DEBUG=true
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=debug
UPLOAD_DIR=/app/uploads
CSV_FILE=/app/data/annotations.csv
ALLOWED_ORIGINS=https://staging.yourdomain.com
```

## Security Considerations

### Production Security Checklist

#### Application Security
- [ ] Disable debug mode (`DEBUG=false`)
- [ ] Configure specific CORS origins (not `*`)
- [ ] Set secure file size limits
- [ ] Enable HTTPS only
- [ ] Configure security headers
- [ ] Validate all file uploads
- [ ] Sanitize CSV data

#### Infrastructure Security
- [ ] Use non-root user for application
- [ ] Configure firewall rules
- [ ] Enable fail2ban for SSH protection
- [ ] Regular security updates
- [ ] Secure file permissions
- [ ] Network security groups
- [ ] SSL/TLS certificates

#### Security Headers

Configure nginx with security headers:

```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com;" always;
```

### File Upload Security

```python
# Enhanced file validation
ALLOWED_MIME_TYPES = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/gif': ['.gif'],
    'image/bmp': ['.bmp'],
    'image/webp': ['.webp']
}

def validate_file_security(file):
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, "Invalid file type"
    
    # Verify file signature
    file_signature = file.read(16)
    file.seek(0)
    
    # Additional security checks
    return True, None
```

## Monitoring and Logging

### Application Logging

Configure structured logging:

```python
# logging_config.py
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/app/logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "json",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Health Monitoring

#### Application Metrics

```python
# metrics.py
from prometheus_client import Counter, Histogram, generate_latest

upload_counter = Counter('uploads_total', 'Total number of uploads')
processing_time = Histogram('processing_seconds', 'Time spent processing')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor system resources
htop              # CPU and memory usage
iotop             # Disk I/O
nethogs           # Network usage
df -h             # Disk space
```

### Log Aggregation

#### Using ELK Stack

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## Backup and Recovery

### Data Backup Strategy

#### File System Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/photo-annotator"
APP_DIR="/opt/photo-annotator/app"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup uploads
tar -czf "$BACKUP_DIR/$DATE/uploads.tar.gz" -C "$APP_DIR" uploads/

# Backup CSV data
cp "$APP_DIR/data/annotations.csv" "$BACKUP_DIR/$DATE/"

# Backup configuration
cp "$APP_DIR/.env" "$BACKUP_DIR/$DATE/"

# Clean old backups (keep last 30 days)
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR/$DATE"
```

#### Database Backup (if migrated)

```bash
#!/bin/bash
# db_backup.sh
pg_dump -h localhost -U photo_annotator photo_annotator_db > "backup_$(date +%Y%m%d_%H%M%S).sql"
```

#### Automated Backup with Cron

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/photo-annotator/scripts/backup.sh

# Weekly full backup at 3 AM on Sundays
0 3 * * 0 /opt/photo-annotator/scripts/full_backup.sh
```

### Recovery Procedures

#### Application Recovery

```bash
#!/bin/bash
# restore.sh

BACKUP_DATE=$1
BACKUP_DIR="/backups/photo-annotator/$BACKUP_DATE"
APP_DIR="/opt/photo-annotator/app"

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: $0 <backup_date>"
    exit 1
fi

# Stop application
sudo systemctl stop photo-annotator

# Restore uploads
sudo -u photo-annotator tar -xzf "$BACKUP_DIR/uploads.tar.gz" -C "$APP_DIR"

# Restore CSV data
sudo -u photo-annotator cp "$BACKUP_DIR/annotations.csv" "$APP_DIR/data/"

# Restore configuration
sudo -u photo-annotator cp "$BACKUP_DIR/.env" "$APP_DIR/"

# Start application
sudo systemctl start photo-annotator

echo "Recovery completed from backup: $BACKUP_DATE"
```

#### Disaster Recovery Plan

1. **Identify the issue**: Check logs and system status
2. **Stop the application**: Prevent further data corruption
3. **Assess data integrity**: Check file system and data files
4. **Restore from backup**: Use most recent valid backup
5. **Test application**: Verify functionality after restore
6. **Monitor closely**: Watch for recurring issues

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000
sudo netstat -tulpn | grep :8000

# Kill process
sudo kill -9 <PID>

# Or use different port
uvicorn src.photo_annotator.main:app --port 8001
```

#### Permission Errors

```bash
# Fix file permissions
sudo chown -R photo-annotator:photo-annotator /opt/photo-annotator
sudo chmod -R 755 /opt/photo-annotator/app/uploads
sudo chmod -R 644 /opt/photo-annotator/app/data
```

#### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean up old files
find /opt/photo-annotator/app/uploads -type f -mtime +365 -delete
find /opt/photo-annotator/app/logs -name "*.log.*" -mtime +30 -delete

# Rotate logs manually
sudo logrotate -f /etc/logrotate.d/photo-annotator
```

#### Memory Issues

```bash
# Check memory usage
free -h
top -p $(pgrep -f "photo-annotator")

# Restart application
sudo systemctl restart photo-annotator

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Debugging Production Issues

#### Enable Debug Logging

```bash
# Temporarily enable debug logging
sudo systemctl edit photo-annotator

# Add override
[Service]
Environment=LOG_LEVEL=debug

# Restart service
sudo systemctl restart photo-annotator
```

#### Application Logs

```bash
# View application logs
sudo journalctl -u photo-annotator -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View application file logs
sudo tail -f /opt/photo-annotator/app/logs/app.log
```

#### Performance Debugging

```bash
# Check system resources
htop
iotop
netstat -tulpn

# Profile application
py-spy top --pid $(pgrep -f "photo-annotator")
```

### Recovery Checklist

When issues occur:

1. [ ] Check service status (`systemctl status photo-annotator`)
2. [ ] Review recent logs (`journalctl -u photo-annotator --since "1 hour ago"`)
3. [ ] Check disk space (`df -h`)
4. [ ] Check memory usage (`free -h`)
5. [ ] Verify file permissions
6. [ ] Test network connectivity
7. [ ] Check nginx configuration (`nginx -t`)
8. [ ] Verify SSL certificates
9. [ ] Test application endpoints
10. [ ] Review recent changes or deployments

This comprehensive deployment guide covers all aspects of deploying the Photo Annotation Tool from development to production environments, including security, monitoring, and recovery procedures.