# Configuration Guide - Eye Donation Pledge System

## Quick Start Configuration

### Development Setup (5 minutes)
```bash
# 1. Copy the example environment file
cp .env.example .env

# 2. Default settings are fine for development
# The .env file provides sensible defaults

# 3. Create admin user
flask create-admin

# 4. Run application
flask run
```

## Production Configuration

### Prerequisites
- PostgreSQL database set up
- Valid SSL/HTTPS certificate
- Strong SECRET_KEY generated

### Environment Variables to Set

#### 1. **Security** (CRITICAL)
```bash
# Generate a strong SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Set in .env
SECRET_KEY=<output-from-above>
SESSION_COOKIE_SECURE=True
```

#### 2. **Database** 
```bash
# PostgreSQL connection string
DATABASE_URL=postgresql://username:password@hostname:5432/eye_pledge_db

# Test connection
flask shell
>>> from app import create_app, db
>>> app = create_app()
>>> db.session.execute('SELECT 1')
```

#### 3. **Institution Information**
```bash
INSTITUTION_NAME=Your Eye Bank Name
INSTITUTION_ADDRESS=Full Address Here
INSTITUTION_PHONE=+91-XXXXXXXXXX
INSTITUTION_EMAIL=contact@institution.org
INSTITUTION_WEBSITE=https://your-domain.org
```

#### 4. **Email (Optional)**
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@eyebank.org
```

### Deployment Checklist

- [ ] PostgreSQL database created
- [ ] SECRET_KEY set and strong
- [ ] DATABASE_URL configured
- [ ] Institution details updated
- [ ] HTTPS/SSL configured
- [ ] SESSION_COOKIE_SECURE=True
- [ ] Email configured (if needed)
- [ ] Admin user created: `flask create-admin`
- [ ] Database migrated: `flask db upgrade`
- [ ] Backups configured
- [ ] Monitoring set up

## Configuration Reference

### Database

| Setting | Value | Notes |
|---------|-------|-------|
| `DATABASE_URL` | Connection string | SQLite for dev, PostgreSQL for prod |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | False | Don't track model changes |

### Security

| Setting | Development | Production |
|---------|------------|-----------|
| `DEBUG` | True | False |
| `SECRET_KEY` | dev-key | Strong random key |
| `SESSION_COOKIE_SECURE` | False | True (with HTTPS) |
| `SESSION_COOKIE_HTTPONLY` | True | True |
| `SESSION_COOKIE_SAMESITE` | Lax | Lax |

### Institution

| Setting | Example |
|---------|---------|
| `INSTITUTION_NAME` | National Eye Bank |
| `INSTITUTION_ADDRESS` | Medical Campus, City |
| `INSTITUTION_PHONE` | +91-1234567890 |
| `INSTITUTION_EMAIL` | info@eyebank.org |
| `INSTITUTION_WEBSITE` | https://eyebank.org |

### Pagination

| Setting | Default | Notes |
|---------|---------|-------|
| `PLEDGES_PER_PAGE` | 20 | Pledges per page in admin list |
| `AUDIT_LOGS_PER_PAGE` | 50 | Audit logs per page |

### Features

| Feature | Default | Status |
|---------|---------|--------|
| `ENABLE_EMAIL_VERIFICATION` | False | Not implemented |
| `ENABLE_OTP_VERIFICATION` | False | Not implemented |
| `ENABLE_DIGITAL_SIGNATURE` | False | Not implemented |
| `ENABLE_API` | False | Not implemented |
| `ENABLE_EXPORT` | True | Working |
| `ENABLE_PRINT` | True | Working |

## Troubleshooting Configuration

### "SECRET_KEY environment variable must be set in production"
**Solution**: Generate and set SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Copy output to .env as SECRET_KEY=...
```

### "Could not locate a Flask application"
**Solution**: Set FLASK_APP
```bash
export FLASK_APP=app.py
# Or add to .env: FLASK_APP=app.py
```

### Database connection errors
**Solution**: Verify DATABASE_URL
```bash
# Test SQLite
sqlite3 eye_pledge.db ".tables"

# Test PostgreSQL
psql postgresql://user:pass@localhost:5432/eye_pledge_db -c "SELECT 1"
```

### Session issues in production
**Solution**: Ensure HTTPS is enabled before setting SESSION_COOKIE_SECURE=True
```bash
# Test HTTPS
curl -I https://your-domain.org
```

## Environment-Specific Configurations

### Development (.env)
```ini
FLASK_ENV=development
DEBUG=True
DATABASE_URL=sqlite:///eye_pledge.db
SESSION_COOKIE_SECURE=False
```

### Staging (.env.staging)
```ini
FLASK_ENV=production
DEBUG=False
DATABASE_URL=postgresql://...
SESSION_COOKIE_SECURE=True
```

### Production (.env.prod)
```ini
FLASK_ENV=production
DEBUG=False
DATABASE_URL=postgresql://...
SESSION_COOKIE_SECURE=True
# All security settings enabled
```

## Best Practices

1. **Never commit .env files** - Use .env.example as template
2. **Use strong SECRET_KEY** - Minimum 32 characters
3. **Enable HTTPS in production** - Before setting SESSION_COOKIE_SECURE=True
4. **Regular backups** - Set up automated daily backups
5. **Monitor logs** - Use systemd journal or log aggregation
6. **Update regularly** - Keep dependencies current
7. **Security audit** - Review configuration monthly

## Support

For configuration issues:
1. Check the logs: `tail -f logs/app.log`
2. Review this guide
3. Check the Flask/SQLAlchemy documentation
4. Check the README.md for additional help

---

**Configuration Complete!** Your system is ready for deployment.
