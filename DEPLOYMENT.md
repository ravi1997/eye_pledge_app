# Production Deployment Guide

Complete guide for deploying Eye Pledge App to production.

## Pre-Deployment Checklist

- [ ] Generate strong SECRET_KEY
- [ ] Set up PostgreSQL database
- [ ] Configure domain/SSL certificate
- [ ] Set all environment variables
- [ ] Test application locally
- [ ] Create database backups strategy
- [ ] Set up monitoring/logging

## 1. Environment Setup

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Output: f3a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### Create .env file

```bash
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=<paste-generated-key-above>
DATABASE_URL=postgresql://user:password@db.example.com:5432/eye_pledge
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password>
INSTITUTION_EMAIL=admin@eyebank.org
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
EOF

chmod 600 .env  # Only owner can read
```

## 2. Database Setup (PostgreSQL)

### Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

### Create Database

```bash
sudo -u postgres psql

# In psql:
CREATE USER eye_pledge_user WITH PASSWORD 'strong-password-here';
CREATE DATABASE eye_pledge OWNER eye_pledge_user;
ALTER ROLE eye_pledge_user SET client_encoding TO 'utf8';
ALTER ROLE eye_pledge_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE eye_pledge_user SET default_transaction_deferrable TO on;
ALTER ROLE eye_pledge_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE eye_pledge TO eye_pledge_user;
\q
```

### Update DATABASE_URL

```
DATABASE_URL=postgresql://eye_pledge_user:password@localhost:5432/eye_pledge
```

## 3. Application Setup

### Clone Repository

```bash
cd /var/www
git clone https://github.com/your-org/eye_pledge_app.git
cd eye_pledge_app
```

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### Initialize Database

```bash
export FLASK_APP=app.py
export FLASK_ENV=production
source .env  # Load environment variables

flask db upgrade
flask create-admin  # Create first admin user
```

## 4. Gunicorn Configuration

### Create gunicorn_config.py

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
accesslog = "/var/log/eye_pledge/access.log"
errorlog = "/var/log/eye_pledge/error.log"
loglevel = "info"
```

### Create systemd Service File

```bash
sudo nano /etc/systemd/system/eye_pledge.service
```

```ini
[Unit]
Description=Eye Donation Pledge App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/eye_pledge_app
ExecStart=/var/www/eye_pledge_app/venv/bin/gunicorn --config gunicorn_config.py "app:create_app()"
Restart=always
RestartSec=10
EnvironmentFile=/var/www/eye_pledge_app/.env

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable eye_pledge
sudo systemctl start eye_pledge
sudo systemctl status eye_pledge
```

## 5. Nginx Configuration

### Install Nginx

```bash
sudo apt-get install nginx
```

### Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/eye_pledge
```

```nginx
server {
    listen 80;
    server_name eyepledge.example.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name eyepledge.example.com;

    # SSL Certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/eyepledge.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/eyepledge.example.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/eye_pledge_access.log;
    error_log /var/log/nginx/eye_pledge_error.log;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90;
    }

    # Static files (if any)
    location /static/ {
        alias /var/www/eye_pledge_app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Limit request size
    client_max_body_size 16M;
}
```

### Enable Nginx Site

```bash
sudo ln -s /etc/nginx/sites-available/eye_pledge /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

## 6. SSL Certificate (Let's Encrypt)

### Install Certbot

```bash
sudo apt-get install certbot python3-certbot-nginx
```

### Generate Certificate

```bash
sudo certbot certonly --nginx -d eyepledge.example.com
```

### Auto-Renewal

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## 7. Database Backups

### Create Backup Script

```bash
mkdir -p /backups/eye_pledge

cat > /home/backup_eye_pledge.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/eye_pledge"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="eye_pledge"

mkdir -p $BACKUP_DIR

pg_dump -U eye_pledge_user $DB_NAME | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/backup_$TIMESTAMP.sql.gz"
EOF

chmod +x /home/backup_eye_pledge.sh
```

### Schedule Backup

```bash
sudo crontab -e

# Add this line (daily at 2 AM):
0 2 * * * /home/backup_eye_pledge.sh
```

## 8. Monitoring & Logging

### View Application Logs

```bash
sudo journalctl -u eye_pledge -f  # Follow mode
sudo journalctl -u eye_pledge --lines=100
```

### View Nginx Logs

```bash
sudo tail -f /var/log/nginx/eye_pledge_access.log
sudo tail -f /var/log/nginx/eye_pledge_error.log
```

### Monitor System Resources

```bash
# Install htop
sudo apt-get install htop
htop

# Check disk space
df -h

# Check memory
free -h
```

## 9. Updates & Maintenance

### Update Application

```bash
cd /var/www/eye_pledge_app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart eye_pledge
```

### Monitor Database Size

```bash
psql -U eye_pledge_user eye_pledge -c "SELECT pg_size_pretty(pg_database.datsize) FROM pg_database WHERE datname = 'eye_pledge';"
```

## 10. Security Hardening

### Firewall Configuration

```bash
sudo ufw enable
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw status
```

### Fail2Ban (Brute Force Protection)

```bash
sudo apt-get install fail2ban

# Create jail for Flask app
sudo nano /etc/fail2ban/jail.d/eye_pledge.conf
```

```ini
[DEFAULT]
findtime = 3600
maxretry = 5

[sshd]
enabled = true

[eye_pledge]
enabled = true
port = http,https
filter = eye_pledge
logpath = /var/log/nginx/eye_pledge_access.log
maxretry = 10
```

## Troubleshooting

### Service won't start
```bash
sudo journalctl -u eye_pledge -n 50
```

### Database connection error
```bash
psql -U eye_pledge_user -h localhost -d eye_pledge
```

### Nginx 502 Bad Gateway
- Check if Gunicorn is running: `sudo systemctl status eye_pledge`
- Check Nginx logs: `sudo tail -f /var/log/nginx/eye_pledge_error.log`

### SSL Certificate issues
```bash
sudo certbot renew --dry-run
sudo certbot renew
```

## Performance Tuning

### PostgreSQL tuning
```sql
-- Edit /etc/postgresql/12/main/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Nginx caching
Add to Nginx config:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=10g inactive=60m use_temp_path=off;

location / {
    proxy_cache my_cache;
    proxy_cache_valid 200 1h;
}
```

## Support & Alerts

### Email Notifications

Configure mail for error alerts:
```bash
sudo apt-get install postfix
```

## Rollback Procedure

If update fails:

```bash
# Rollback database
flask db downgrade

# Revert code
git revert <commit>

# Restart
sudo systemctl restart eye_pledge
```
