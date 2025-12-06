#!/bin/bash
# Database initialization script for Eye Pledge App

echo "================================"
echo "Eye Donation Pledge App - Setup"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source env/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Initialize database
echo "Initializing database..."
flask db upgrade 2>/dev/null || flask db init && flask db upgrade
echo "✓ Database initialized"

# Create admin user
echo ""
echo "Create Admin User"
echo "=================="
flask create-admin

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Run: flask run"
echo "2. Visit: http://localhost:5000"
echo "3. Admin Login: http://localhost:5000/admin/login"
echo ""
