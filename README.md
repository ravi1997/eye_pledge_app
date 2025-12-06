# Eye Donation Pledge Form System

A production-ready Flask web application for digitizing eye donation pledges. Designed for the National Eye Bank / Eye Donation Centers to streamline pledge registration, verification, and management.

## Features

### Public Features
- **Online Pledge Form**: Comprehensive form to capture donor information, address, witness details, and consent
- **Real-time Validation**: Client-side and server-side validation for all inputs
- **Unique Reference Numbers**: Auto-generated reference numbers for each pledge (format: NEB-2025-000001)
- **Success Confirmation**: Donors receive a confirmation page with reference number
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

### Admin Features
- **Secure Authentication**: Simple username/password based login with session management
- **Dashboard**: Overview of pledges with statistics and trend analysis
- **Search & Filter**: Search by name, mobile, email, reference number; filter by status, state, date range
- **Pledge Management**: View complete pledge details, mark verified/unverified
- **CSV Export**: Export filtered pledges for analysis and backup
- **Print/PDF**: Print-friendly version of each pledge resembling original paper form
- **Soft Delete**: Deactivate pledges without hard deletion for audit trails
- **Audit Logging**: Track admin actions (verification, export, deactivation)

## Tech Stack

- **Framework**: Flask 3.0.3
- **ORM**: SQLAlchemy 2.0.44
- **Database**: SQLite (development), supports PostgreSQL (production)
- **Database Migrations**: Flask-Migrate 4.0.7
- **Frontend**: Bootstrap 5.3.0, Jinja2 templates
- **Authentication**: Werkzeug (password hashing)

## Project Structure

```
eye_pledge_app/
├── app.py                      # Main application with all routes
├── models.py                   # Database models
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── eye_pledge.db              # SQLite database (created on first run)
├── migrations/                # Database migration scripts (Alembic)
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
├── templates/                 # Jinja2 HTML templates
│   ├── base.html             # Base template with navbar and footer
│   ├── index.html            # Home page
│   ├── pledge_form.html      # Main pledge form
│   ├── pledge_view.html      # Public pledge view
│   ├── success.html          # Pledge success page
│   ├── 404.html              # Not found page
│   ├── 500.html              # Server error page
│   └── admin/
│       ├── login.html        # Admin login page
│       ├── dashboard.html    # Admin dashboard
│       ├── pledges_list.html # Admin pledges list
│       ├── pledge_detail.html # Admin pledge details
│       └── pledge_print.html # Print/PDF template
├── static/                    # CSS, JS, images (if any)
└── uploads/                   # File uploads directory
```

## Installation & Setup

### 1. Clone or Navigate to Project

```bash
cd /path/to/eye_pledge_app
```

### 2. Create Virtual Environment

```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
export FLASK_APP=app.py
export FLASK_ENV=development

# Create database tables
flask db init       # First time only (already initialized)
flask db upgrade    # Apply migrations
```

### 5. Create Admin User

```bash
flask create-admin
```

You'll be prompted to enter:
- Username
- Password
- Full Name
- Email

Example:
```
Username: admin
Password: ChangeMe@123
Full Name: Admin User
Email: admin@eyebank.org
```

### 6. Run Application

```bash
flask run
```

The application will be available at `http://127.0.0.1:5000`

## Usage Guide

### For Donors

1. **Home Page** (`/`): Learn about eye donation
2. **Pledge Form** (`/pledge`): Fill out the comprehensive pledge form
   - Donor details (name, age, contact)
   - Address information
   - Pledge consent
   - Witness information
3. **Success Page**: Receive confirmation and reference number
4. **View Pledge** (`/pledge/<reference>/view`): View saved pledge information

### For Admins

1. **Login** (`/admin/login`):
   - Username: `admin`
   - Password: (as set during setup)

2. **Dashboard** (`/admin/dashboard`):
   - View statistics
   - See trends by month and state
   - Quick access to features

3. **Manage Pledges** (`/admin/pledges`):
   - Search by name, mobile, email, reference number
   - Filter by verification status
   - Filter by state and date range
   - Click "View" to see full details

4. **Pledge Details** (`/admin/pledge/<id>`):
   - View complete information
   - Mark as verified/unverified
   - Print or save as PDF
   - Deactivate pledge

5. **Export** (`/admin/export`):
   - Export filtered results as CSV
   - Useful for reports and analysis

## Database Models

### EyeDonationPledge
Main model storing pledge information:
- **Donor Details**: Name, gender, DOB, blood group, contact info
- **Address Details**: Full address with pincode and state
- **Pledge Details**: Date, organs consented, language, notes
- **Witness 1**: Next of kin information (mandatory)
- **Witness 2**: Optional additional witness
- **System Fields**: Created/updated timestamps, verification status, reference number

### AdminUser
Admin account model:
- Username, password hash
- Email, full name
- Active status, last login timestamp

### AuditLog
Audit trail for admin actions:
- Admin user, pledge reference
- Action type, details
- Timestamp

## API / Future Enhancements

The system is designed to easily accommodate these future additions:

1. **REST API Endpoints**: Blueprint structure ready for `/api/pledges/` endpoints
2. **Digital Signature Capture**: Fields `donor_consent_checkbox`, `witness1_consent_checkbox` ready
3. **OTP Verification**: Fields `donor_mobile_verified`, `donor_mobile_verified_at` ready
4. **Email Confirmations**: Fields `donor_email_confirmed`, `donor_email_confirmed_at` ready
5. **QR Codes**: Can be added to PDF generation
6. **Multilingual Support**: Template structure supports i18n
7. **SMS Notifications**: Ready for integration with SMS gateway

## Configuration

Edit `config.py` to customize:

```python
# Institution details
INSTITUTION_NAME = "National Eye Bank"
INSTITUTION_ADDRESS = "Dr. RP Centre, AIIMS, New Delhi"
INSTITUTION_PHONE = "+91-11-XXXX-XXXX"
INSTITUTION_EMAIL = "eyebank@aiims.edu.in"

# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///eye_pledge.db'  # For PostgreSQL: postgresql://user:pass@localhost/dbname

# Pagination
PLEDGES_PER_PAGE = 20

# Default consent text
DEFAULT_CONSENT_TEXT = "..."
```

## Environment Variables (Production)

Set these for production deployment:

```bash
export FLASK_ENV=production
export SECRET_KEY=your-very-secure-secret-key-here
export DATABASE_URL=postgresql://user:password@localhost/eye_pledge_prod
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=your-strong-password
```

## Database Migrations

When you modify models, create and apply migrations:

```bash
# Create migration
flask db migrate -m "Description of changes"

# Review migration in migrations/versions/

# Apply migration
flask db upgrade

# Rollback if needed
flask db downgrade
```

## Common Tasks

### Reset Database (WARNING: Deletes all data)
```bash
flask reset-db
```

### Create Another Admin User
```bash
flask create-admin
```

### View Database Schema
```bash
sqlite3 eye_pledge.db ".schema"
```

### Export Pledges to CSV (CLI)
```bash
# Use admin panel export feature, or write a CLI command
```

## Security Considerations

1. **CSRF Protection**: All forms include CSRF tokens (future: enable Flask-WTF)
2. **Password Hashing**: Werkzeug passwords are hashed with strong algorithms
3. **Session Security**: Secure session cookies with HTTPOnly and SameSite flags
4. **Input Validation**: Server-side validation on all inputs
5. **SQL Injection**: SQLAlchemy parameterized queries prevent SQL injection
6. **Secrets**: Use environment variables for SECRET_KEY and passwords

## Deployment

### Using Gunicorn (Recommended)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### With Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name eyepledge.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### With Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app()"]
```

Build and run:
```bash
docker build -t eye-pledge .
docker run -p 8000:8000 -e SECRET_KEY=... eye-pledge
```

## Troubleshooting

### Database Locked Error
- SQLite can lock under concurrent access. Use PostgreSQL for production.

### "No module named 'flask'"
- Ensure virtual environment is activated: `source env/bin/activate`
- Install requirements: `pip install -r requirements.txt`

### Admin Login Fails
- Verify user was created: `flask create-admin`
- Check password is correct
- Reset password by deleting user and creating new one

### Form Validation Errors
- Check console for validation messages
- Ensure all required fields are filled
- Check email/mobile format

## File Sizes & Performance

- **Typical pledge record**: ~2-3 KB
- **10,000 pledges**: ~20-30 MB SQLite database
- **100,000 pledges**: Recommend PostgreSQL

## Support & Contact

For issues or questions, contact:
- Email: {{ institution_email }}
- Address: {{ institution_address }}

## License

This application is designed for eye donation centers. Use and modify as needed.

## Changelog

### Version 1.0.0 (Current)
- Initial release
- Public pledge form
- Admin dashboard
- Search, filter, export
- Print/PDF functionality
- Basic authentication
