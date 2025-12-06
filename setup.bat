@echo off
REM Database initialization script for Eye Pledge App (Windows)

echo.
echo ================================
echo Eye Donation Pledge App - Setup
echo ================================
echo.

REM Check if virtual environment exists
if not exist "env" (
    echo Creating virtual environment...
    python -m venv env
    echo OK: Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call env\Scripts\activate.bat
echo OK: Virtual environment activated

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
echo OK: Dependencies installed

REM Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Initialize database
echo Initializing database...
flask db upgrade >nul 2>&1 || (flask db init && flask db upgrade)
echo OK: Database initialized

REM Create admin user
echo.
echo Create Admin User
echo ====================
flask create-admin

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Run: flask run
echo 2. Visit: http://localhost:5000
echo 3. Admin Login: http://localhost:5000/admin/login
echo.
pause
