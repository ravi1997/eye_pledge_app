# Eye Donation Pledge Form System

A production-ready Flask web application for digitizing eye donation pledges, designed for Eye Donation Centers.

## Quick Start (User & Admin Guide)

This guide is for administrators and users of the system. 
- **For a detailed User Manual with screenshots and flows, see [USER_MANUAL.md](USER_MANUAL.md).**
- **For technical details and architecture, see [DEVELOPER.md](DEVELOPER.md).**

### Key Features
- **Public**: Mobile-responsive pledge form, real-time validation, and certificate generation.
- **Admin**: Dashboard statistics, pledge management, PDF export, and audit logging.
- **Security**: Role-based access, encrypted sessions, and comprehensive logging.

## Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd eye_pledge_app

# Create virtual environment
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
1. Initialize the database:
   ```bash
   flask db upgrade
   ```
2. Create an admin account:
   ```bash
   flask create-admin
   # Follow the prompts to set username and password
   ```

### 4. Running the Application
```bash
flask run
```
Access the application at: `http://127.0.0.1:5000`

## Usage Guide

### For Donors
- Navigate to the **Home Page** to learn about donation.
- Click **Start Pledging** to fill out the form.
- You will need:
    - Personal ID details (Aadhaar/PAN etc.)
    - One Witness (Next of Kin recommended) details.
- After submission, save your **Reference Number**.

### For Admins
- Login at `/admin/login`.
- **Dashboard**: View daily statistics and recent activity.
- **Pledges**: View, verify, or print individual pledges.
- **Logs**: Monitor system access and security events.

## Support
For technical support or feature requests, please contact the development team or refer to `DEVELOPER.md`.
