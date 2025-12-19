# Developer Documentation

This document provides technical details for developers contributing to the Eye Donation Pledge application.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Database Schema](#database-schema)
4. [Key Subsystems](#key-subsystems)
   - [Logging](#1-logging-system)
   - [Translations](#2-translation-system)
   - [Authentication](#3-authentication)
5. [Development Workflow](#development-workflow)

---

## Architecture Overview

The application is built using **Flask**, a lightweight WSGI web application framework. It follows a monolithic architecture where the frontend (Jinja2 templates) and backend (Flask routes) are tightly coupled.

### Core Technologies
- **Backend**: Python 3.x, Flask 3.0.3
- **Database**: SQLAlchemy ORM (SQLite for dev, PostgreSQL supported for prod)
- **Frontend**: Bootstrap 5, Jinja2
- **Migrations**: Flask-Migrate (Alembic)

---

## Project Structure

```text
eye_pledge_app/
├── app.py                  # Entry point & Application Factory
├── models.py               # Database Models (SQLAlchemy)
├── translations.py         # Static translation dictionaries (En/Hi)
├── config.py               # Configuration classes
├── migrations/             # Database migration scripts
├── static/                 # CSS, JS, Images
├── templates/              # HTML Templates
│   ├── admin/              # Admin-specific templates
│   └── ...                 # Public templates
└── logs/                   # Application log files
```

---

## Database Schema

The database logic is defined in `models.py`.

### 1. EyeDonationPledge
The core model storing donor information.
- **PK**: `id`
- **Key Fields**: `reference_number` (Unique), `donor_name`, `donor_mobile`, `consent_given`.
- **Witnesses**: Stores details for 2 witnesses directly on the record.
- **Status**: `is_active`, `is_verified`, `verified_by`.

### 2. AdminUser
Handles administrative access.
- **Fields**: `username`, `password_hash`, `email`.
- **Security**: Passwords hashed using Werkzeug.

### 3. SystemLog
A centralized logging table for the application.
- **Fields**: `log_type` (ACCESS, ERROR, SECURITY, etc.), `level`, `message`, `details`.
- **Purpose**: Allows admins to view logs directly from the dashboard.

### 4. AuditLog
Tracks specific admin actions on pledges.
- **Fields**: `action`, `admin_user_id`, `pledge_id`.

---

## Key Subsystems

### 1. Logging System
The application uses a **Dual Logging Strategy** defined in `app.py`:
1.  **File Logging**: Rotated logs in `logs/` directory (application.log, security.log, etc.).
2.  **Database Logging**: Important events are also written to the `SystemLog` table.

**Helper Function**: `log_system_event(log_type, message, ...)`
Use this function for all logging to ensure it goes to both destinations.

### 2. Translation System
Located in `translations.py` and via `inject_translations` in `app.py`.
- **Mechanism**: A simple dictionary lookup based on session language.
- **Usage**: In templates, use `{{ _('key') }}`.
- **Adding Languages**: Add a new key to the `TRANSLATIONS` dict in `translations.py` and ensure all keys match existing English keys.

### 3. Authentication
- **Admin Implementation**: Custom session-based auth.
- **Decorator**: `@login_required` checks for `admin_user_id` in `session`.
- **Session Security**: Handled by Flask's secure cookie session (configure `SECRET_KEY` in production).

---

## Development Workflow

### Setting up the Environment
1.  Create virtual env: `python -m venv env`
2.  Activate: `source env/bin/activate`
3.  Install: `pip install -r requirements.txt`

### Database Migrations
When modifying `models.py`, use Flask-Migrate:
```bash
flask db migrate -m "Added new field"
flask db upgrade
```

### Running CLI Commands
Internal commands are defined in `app.py` under `@app.cli.command()`.
- `flask create-admin`: Interactive admin creation.
- `flask reset-db`: Drops and recreates tables (Data Loss!).
- `flask init-db`: Creates tables if missing.

### Code Style
- Follow **PEP 8**.
- Ensure all business logic validation happens in `validate_pledge()` inside `app.py`.

---

## Deployment Notes

- **Production Config**: Set `FLASK_ENV=production`.
- **WSGI**: Use Gunicorn.
- **Secrets**: NEVER commit `SECRET_KEY` or production DB headers. Use environment variables.
