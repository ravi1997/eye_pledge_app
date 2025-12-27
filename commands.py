
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from models import db, AdminUser, SystemLog
import getpass

@click.command('create-admin')
@click.option('--username', prompt=True, help='The username for the admin user.')
@click.option('--email', prompt=True, help='The email address for the admin user.')
@click.option('--fullname', prompt='Full Name', help='The full name of the admin user.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password for the admin user.')
@with_appcontext
def create_admin_command(username, email, fullname, password):
    """Create a new admin user."""
    
    # Check if user already exists
    if AdminUser.query.filter_by(username=username).first():
        click.echo(f"Error: User '{username}' already exists.")
        return
    
    if AdminUser.query.filter_by(email=email).first():
        click.echo(f"Error: Email '{email}' is already registered.")
        return

    hashed_password = generate_password_hash(password)
    
    new_admin = AdminUser(
        username=username,
        password_hash=hashed_password,
        email=email,
        full_name=fullname,
        is_active=True
    )
    
    try:
        db.session.add(new_admin)
        db.session.commit()
        
        # Log the event (optional, but good practice if you have system logging)
        # We can try to use the system log if available, or just print
        click.echo(f"Successfully created admin user: {username}")
        
    except Exception as e:
        db.session.rollback()
        click.echo(f"Error creating user: {e}")
