# Quick Start Guide

Get the Eye Pledge App running in 5 minutes!

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Step 1: Activate Virtual Environment

```bash
cd eye_pledge_app
source env/bin/activate
# On Windows: env\Scripts\activate
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Initialize Database

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask db upgrade
```

## Step 4: Create Admin Account

```bash
flask create-admin
```

Example input:
```
Username: admin
Password: admin123
Full Name: System Administrator
Email: admin@eyebank.org
```

## Step 5: Run the Application

```bash
flask run
```

## Step 6: Access the Application

Open your browser and visit:

- **Public Site**: http://localhost:5000
- **Pledge Form**: http://localhost:5000/pledge
- **Admin Login**: http://localhost:5000/admin/login
  - Username: `admin`
  - Password: (as set in Step 4)

## Testing the Application

### Test as Donor

1. Go to http://localhost:5000
2. Click "Start Pledging" or "Pledge Form"
3. Fill out the form with test data:
   - Name: John Doe
   - Mobile: 9876543210
   - Email: john@example.com
   - Address: Test Address, New Delhi
   - City: New Delhi
   - State: Delhi
   - Pincode: 110002
   - Check "I agree and understand..."
   - Submit

4. Note the reference number on success page

### Test as Admin

1. Go to http://localhost:5000/admin/login
2. Login with credentials from Step 4
3. View dashboard with statistics
4. Go to "View All Pledges"
5. Search for the pledge you just created
6. Click "View" to see details
7. Click "Mark as Verified" to verify
8. Click "Print/PDF" to view printable version
9. Use "Export as CSV" to download data

## Common Commands

```bash
# Start server
flask run

# Reset database (WARNING: loses all data)
flask reset-db

# Create another admin user
flask create-admin

# View app configuration
flask config

# Database shell
flask shell
```

## File Locations

- **Database**: `eye_pledge.db` (in project root)
- **Templates**: `templates/` folder
- **Database Schema**: `models.py`
- **Routes**: `app.py`
- **Configuration**: `config.py`

## Accessing Different Pages

| Page | URL | Access |
|------|-----|--------|
| Home | / | Public |
| Pledge Form | /pledge | Public |
| Success | /success/<ref> | Public |
| View Pledge | /pledge/<ref>/view | Public |
| Admin Login | /admin/login | Public |
| Admin Dashboard | /admin/dashboard | Admin Only |
| Manage Pledges | /admin/pledges | Admin Only |
| Pledge Details | /admin/pledge/<id> | Admin Only |
| Print Pledge | /admin/pledge/<id>/print | Admin Only |

## Troubleshooting

**Error: "No such table: eye_donation_pledges"**
```bash
flask db upgrade
```

**Error: "Failed to locate admin user"**
- Create admin: `flask create-admin`

**Port 5000 already in use**
```bash
flask run --port 5001
```

**Static CSS not loading**
- Ensure templates are in `templates/` folder
- Restart Flask server

## Next Steps

1. Read the full README.md for complete documentation
2. Customize institution details in `config.py`
3. Test all features
4. Deploy to production using Gunicorn + Nginx

## Support

Refer to README.md for detailed documentation and troubleshooting.
