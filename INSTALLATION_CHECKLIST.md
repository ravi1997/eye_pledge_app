# ✅ Installation & Deployment Checklist

## Pre-Installation Checks
- [ ] Python 3.8+ installed
- [ ] pip available
- [ ] Virtual environment created (env/)
- [ ] Git initialized (if needed)

## Installation Steps

### Step 1: Activate Virtual Environment
```bash
source env/bin/activate  # Linux/macOS
# or
env\Scripts\activate  # Windows
```
- [ ] Prompt shows (env) prefix

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```
- [ ] No errors during installation
- [ ] All 5 packages installed

### Step 3: Initialize Database
```bash
export FLASK_APP=app.py
flask db upgrade
```
- [ ] eye_pledge.db file created
- [ ] No migration errors

### Step 4: Create Admin User
```bash
flask create-admin
```
Enter when prompted:
- [ ] Username: (remember this!)
- [ ] Password: (remember this!)
- [ ] Full name: Your Name
- [ ] Email: your@email.com
- [ ] Success message displayed

### Step 5: Run Application
```bash
flask run
```
- [ ] "Running on http://127.0.0.1:5000" message
- [ ] No errors in console

## Testing Steps

### Test 1: Home Page
- [ ] Visit http://localhost:5000
- [ ] Page loads without errors
- [ ] Navigation bar visible
- [ ] "Start Pledging" button present

### Test 2: Public Pledge Form
- [ ] Click "Start Pledging"
- [ ] All form fields visible
- [ ] 6 sections expandable
- [ ] Date picker works
- [ ] Form validation works (try submitting empty)

### Test 3: Form Submission
- [ ] Fill all required fields
- [ ] Click Submit
- [ ] Success page displays
- [ ] Reference number shown (NEB-2025-XXXXXX)
- [ ] Can view pledge summary

### Test 4: Admin Login
- [ ] Visit http://localhost:5000/admin/login
- [ ] Login form visible
- [ ] Enter username and password from Step 4
- [ ] Click Login
- [ ] Redirected to dashboard

### Test 5: Admin Dashboard
- [ ] Statistics cards visible
- [ ] Monthly chart displayed
- [ ] Top states list shown
- [ ] "View All Pledges" button present

### Test 6: Admin Pledges List
- [ ] Click "View All Pledges"
- [ ] Pledges table displayed
- [ ] Search form visible
- [ ] Can search by name
- [ ] Can filter by state
- [ ] Pagination works

### Test 7: Pledge Details
- [ ] Click on a pledge row
- [ ] Full pledge details displayed
- [ ] "Mark as Verified" button present
- [ ] Print button works
- [ ] Verify action logs audit

### Test 8: Admin Features
- [ ] Export to CSV works
- [ ] Print preview loads
- [ ] Unverify action works
- [ ] Deactivate option present

### Test 9: Data Verification
- [ ] Check database for records:
  ```bash
  sqlite3 eye_pledge.db "SELECT COUNT(*) FROM eye_donation_pledges;"
  ```
- [ ] Records count > 0
- [ ] Check admin user exists:
  ```bash
  sqlite3 eye_pledge.db "SELECT * FROM admin_users;"
  ```

## Production Preparation

### Pre-Production Setup
- [ ] Read DEPLOYMENT.md
- [ ] Choose production database (PostgreSQL recommended)
- [ ] Update DATABASE_URL in config.py
- [ ] Set SECRET_KEY environment variable
- [ ] Set INSTITUTION_* variables
- [ ] Set ADMIN_* variables
- [ ] Disable DEBUG mode
- [ ] Set FLASK_ENV=production

### SSL/HTTPS Setup
- [ ] Obtain SSL certificate
- [ ] Configure Nginx for HTTPS
- [ ] Update SESSION_COOKIE_SECURE=True
- [ ] Test HTTPS connection

### Backup & Monitoring
- [ ] Set up automated daily backups
- [ ] Configure monitoring alerts
- [ ] Set up log aggregation
- [ ] Test backup restoration

### Performance Optimization
- [ ] Enable database indexing
- [ ] Configure pagination
- [ ] Set up caching if needed
- [ ] Monitor query performance

## Troubleshooting

### Common Issues

**Issue**: "ModuleNotFoundError: No module named 'flask'"
```bash
# Solution: Install requirements
pip install -r requirements.txt
```

**Issue**: "ERROR: Unable to open database file"
```bash
# Solution: Initialize database
flask db upgrade
```

**Issue**: "RuntimeError: Working outside of request context"
```bash
# Solution: Run flask run instead of python app.py
flask run
```

**Issue**: "Invalid username or password"
```bash
# Solution: Create admin user again
flask create-admin
```

**Issue**: Port 5000 already in use
```bash
# Solution: Use different port
flask run --port 5001
```

## Verification Commands

```bash
# Check Python version
python --version

# Check Flask installation
python -c "import flask; print(flask.__version__)"

# Check database connection
sqlite3 eye_pledge.db "SELECT sqlite_version();"

# Count pledges
sqlite3 eye_pledge.db "SELECT COUNT(*) FROM eye_donation_pledges;"

# List admin users
sqlite3 eye_pledge.db "SELECT username FROM admin_users;"

# Check app runs
flask run --help
```

## Final Verification

Before considering installation complete:
- [ ] All installation steps completed
- [ ] All tests passed
- [ ] No errors in console
- [ ] Database has at least 1 pledge record
- [ ] Admin can login
- [ ] Admin can view all features
- [ ] Public can submit pledges
- [ ] Export CSV works

## Documentation Review

- [ ] Read QUICKSTART.md
- [ ] Read README.md
- [ ] Read DEPLOYMENT.md
- [ ] Review PROJECT_SUMMARY.md
- [ ] Review UPDATE_SUMMARY.md

## Post-Installation Steps

1. **Customize Configuration**
   - [ ] Update INSTITUTION_NAME
   - [ ] Update INSTITUTION_ADDRESS
   - [ ] Update INSTITUTION_EMAIL
   - [ ] Update INSTITUTION_PHONE

2. **Set Environment Variables** (Production)
   - [ ] Create .env file with secrets
   - [ ] Set DATABASE_URL
   - [ ] Set SECRET_KEY
   - [ ] Set FLASK_ENV=production

3. **Plan for Scale**
   - [ ] Set up PostgreSQL (for >100k pledges)
   - [ ] Plan backup strategy
   - [ ] Plan monitoring strategy
   - [ ] Plan migration path

4. **Security Review**
   - [ ] Change default admin password
   - [ ] Review security settings
   - [ ] Enable HTTPS in production
   - [ ] Set up SSL certificates

## Maintenance Checklist

**Daily**
- [ ] Monitor error logs
- [ ] Check database size
- [ ] Monitor CPU/Memory usage

**Weekly**
- [ ] Backup database
- [ ] Review audit logs
- [ ] Check for updates

**Monthly**
- [ ] Full database backup
- [ ] Security audit
- [ ] Performance review
- [ ] Update dependencies (if needed)

---

**Installation Status**: ✅ Complete
**Ready for**: Development & Testing
**Next**: Read QUICKSTART.md for usage guide

Date: December 6, 2025
