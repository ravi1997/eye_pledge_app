from datetime import datetime, timedelta
from functools import wraps
import os
import csv
from io import StringIO

from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, send_from_directory, Response, has_request_context
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import EyeDonationPledge, AdminUser, AuditLog, SystemLog, db
from translations import get_translation

import logging
import sys
from logging import Formatter

from logging import Formatter
from logging.handlers import RotatingFileHandler
import os

# ========================
# Logging Configuration
# ========================
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup as many loggers as you want"""
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File Handler (Rotating)
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, log_file), 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Stream Handler (Console)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger

# Create segregated loggers
app_logger = setup_logger('app_logger', 'application.log')
security_logger = setup_logger('security_logger', 'security.log')
access_logger = setup_logger('access_logger', 'access.log')
error_logger = setup_logger('error_logger', 'error.log')
auth_logger = setup_logger('auth_logger', 'auth.log')

migrate = Migrate()


def create_app(config_name='development'):
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'development':
        app.config.from_object(Config)
    else:
        app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models from external file if exists, otherwise define here
    
    app.EyeDonationPledge = EyeDonationPledge
    app.AdminUser = AdminUser
    app.AuditLog = AuditLog

    # ========================
    # Authentication Decorator
    # ========================
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'admin_user_id' not in session:
                flash('Please log in first', 'warning')
                return redirect(url_for('admin_login'))
            return f(*args, **kwargs)
        return decorated_function

    # ========================
    # Context Processors
    # ========================
    @app.context_processor
    def inject_institution():
        return {
            'institution_name': app.config.get('INSTITUTION_NAME', 'Eye Bank'),
            'institution_email': app.config.get('INSTITUTION_EMAIL', 'info@eyebank.org'),
            'institution_phone': app.config.get('INSTITUTION_PHONE', '+91-1234567890'),
        }

    @app.context_processor
    def inject_language_helper():
        def translate(text):
            lang = session.get('lang', 'English')
            return get_translation(text, lang)
        return dict(_=translate)

    # ========================
    # Error Handlers
    # ========================
    @app.errorhandler(404)
    def page_not_found(e):
        return safe_render('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return safe_render('500.html'), 500

    # ========================
    # Comprehensive Logging Helper
    # ========================
    def log_system_event(log_type, message, level='INFO', module=None, user_id=None, details=None):
        """
        Unified helper to log to File AND Database.
        """
        # 0. Auto-detect User ID if not provided
        if user_id is None and has_request_context():
            user_id = session.get('admin_user_id')

        # 1. Map type to specific logger
        target_logger = app_logger
        if log_type == 'SECURITY': target_logger = security_logger
        elif log_type == 'ACCESS': target_logger = access_logger
        elif log_type == 'ERROR': target_logger = error_logger
        elif log_type == 'AUTH': target_logger = auth_logger
        
        # 2. File Log
        log_msg = f"[{log_type}] {message}"
        if level == 'WARNING': target_logger.warning(log_msg)
        elif level == 'ERROR': target_logger.error(log_msg)
        elif level == 'CRITICAL': target_logger.critical(log_msg)
        else: target_logger.info(log_msg)
        
        # 3. Database Log (SystemLog)
        try:
            if db.session:
                system_log = SystemLog(
                    log_type=log_type,
                    level=level,
                    message=message,
                    module=module,
                    user_id=user_id,
                    ip_address=request.remote_addr if has_request_context() else None,
                    details=str(details) if details else None
                )
                db.session.add(system_log)
                db.session.commit()
        except Exception as e:
            error_logger.error(f"Failed to write to SystemLog DB: {e}")

    def log_security_event(event_type, message, level='INFO', user_id=None, pledge_id=None):
        """Backward compatibility wrapper for existing code"""
        details = f"PledgeID: {pledge_id}" if pledge_id else None
        log_system_event('SECURITY', f"{event_type}: {message}", level=level.upper(), user_id=user_id, details=details)

    # ========================
    # Access Logging Hooks
    # ========================
    @app.after_request
    def log_request_info(response):
        if request.path.startswith('/static') or request.path.endswith('favicon.ico'):
            return response
        
        # Build comprehensive details
        details_list = []
        
        # 1. User Agent
        if request.user_agent:
            details_list.append(f"UA: {request.user_agent.string[:50]}...") # Truncate for brevity
            
        # 2. Referrer
        if request.referrer:
            details_list.append(f"Ref: {request.referrer}")
            
        # 3. Query Args
        if request.args:
            details_list.append(f"Args: {dict(request.args)}")
            
        # 4. Blueprint/View
        if request.endpoint:
            details_list.append(f"View: {request.endpoint}")

        details_str = " | ".join(details_list)

        log_system_event(
            'ACCESS', 
            f"{request.method} {request.path} {response.status_code}", 
            level='INFO',
            details=details_str
        )
        return response

    # ========================
    # Utility Functions
    # ========================
    def generate_reference_number():
        """Generate unique reference number: NEB-YYYY-XXXXXX"""
        year = datetime.now().year
        last_pledge = EyeDonationPledge.query.filter_by(is_active=True).order_by(
            EyeDonationPledge.id.desc()
        ).first()
        
        sequence = 1 if not last_pledge else last_pledge.id + 1
        return f"NEB-{year}-{sequence:06d}"

    def parse_date(date_str):
        """Parse date string to date object"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return None

    def parse_time(time_str):
        """Parse time string to time object"""
        if not time_str:
            return None
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except:
            return None

    def validate_pledge(form_data):
        """Server-side validation of pledge form"""
        errors = []
        
        # Required fields
        if not form_data.get('donor_name'):
            errors.append('Donor name is required')
        if not form_data.get('address_line1'):
            errors.append('Address is required')
        if not form_data.get('city'):
            errors.append('City is required')
        if not form_data.get('state'):
            errors.append('State is required')
        if not form_data.get('pincode'):
            errors.append('Pincode is required')
        if not form_data.get('donor_mobile'):
            errors.append('Mobile number is required')
        # Email is optional in UI, so removing required check
        # if not form_data.get('donor_email'):
        #     errors.append('Email is required')
        if not form_data.get('witness1_name'):
            errors.append('Witness 1 name is required')
        if not form_data.get('donor_consent'):
            errors.append('Consent must be given')
        
        # Email validation
        if form_data.get('donor_email') and '@' not in form_data.get('donor_email', ''):
            errors.append('Invalid email address')
        
        # Mobile validation
        if form_data.get('donor_mobile') and not form_data.get('donor_mobile').isdigit():
            errors.append('Mobile number must contain only digits')
        
        # Log validation errors
        if errors:
            app_logger.warning(f"Validation failed: {errors}")
        else:
            app_logger.info("Validation passed")
        
        return errors

    def safe_render(template_name, **context):
        """Render a template and catch rendering exceptions to avoid crashing routes."""
        try:
            return render_template(template_name, **context)
        except Exception as e:
            app_logger.exception(f"Template render error for {template_name}: {e}")
            app_logger.error(f"Template render error: {e}")
            try:
                return render_template('500.html'), 500
            except Exception:
                # If even the 500 page fails, return a minimal response
                return ("An internal error occurred while rendering the page.", 500)

    # ========================
    # PUBLIC ROUTES
    # ========================
    @app.route("/")
    def index():
        """Home page"""
        pledge_count = EyeDonationPledge.query.filter_by(is_active=True).count()
        return safe_render('index.html', 
                address = app.config.get('INSTITUTION_ADDRESS', 'Eye Bank'),
                
                active_page='home', 
                current_year=datetime.now().year,
                pledge_count=pledge_count)

    @app.route("/favicon.ico")
    def favicon():
        """Favicon"""
        return send_from_directory(os.path.join(app.root_path, 'static', 'image'),
                                 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route("/set-language/<lang>")
    def set_language(lang):
        """Set the language preference in session"""
        if lang in ['English', 'Hindi']:
            session['lang'] = lang
        
        # Redirect back to the page the user came from, or home
        return redirect(request.referrer or url_for('index'))

    @app.route("/pledge", methods=["GET", "POST"])
    def pledge_form():
        """Pledge form - display and submit"""
        app_logger.info(f"Pledge route accessed via {request.method}")
        
        if request.method == "POST":
            app_logger.info("Processing pledge submission")
            # Log form data (be careful with PII in production, but helpful for debug)
            app_logger.debug(f"Form data keys: {list(request.form.keys())}")
            
            # Validate
            errors = validate_pledge(request.form)
            if errors:
                for error in errors:
                    flash(error, 'danger')
                app_logger.warning(f"Validation errors found, rendering form again: {errors}")
                return safe_render('pledge_form.html', form_data=request.form)
            
            app_logger.info("Validation successful, attempting to save to DB")
            try:
                # Generate reference number
                ref_num = generate_reference_number()
                
                # Get preferred language from session or default to English
                selected_lang = session.get('lang', 'English')

                # Create pledge
                pledge = EyeDonationPledge(
                    reference_number=ref_num,
                    donor_name=request.form.get('donor_name'),
                    donor_gender=request.form.get('gender'),
                    donor_dob=parse_date(request.form.get('date_of_birth')),
                    donor_age=int(request.form.get('age') or 0),
                    donor_blood_group=request.form.get('blood_group'),
                    donor_mobile=request.form.get('donor_mobile'),
                    donor_email=request.form.get('donor_email'),
                    donor_marital_status=request.form.get('marital_status'),
                    donor_occupation=request.form.get('occupation'),
                    donor_id_proof_type=request.form.get('id_proof_type'),
                    donor_id_proof_number=request.form.get('id_proof_number'),
                    
                    # Address
                    address_line1=request.form.get('address_line1'),
                    address_line2=request.form.get('address_line2'),
                    city=request.form.get('city'),
                    district=request.form.get('district'),
                    state=request.form.get('state'),
                    pincode=request.form.get('pincode'),
                    country=request.form.get('country', 'India'),
                    
                    # Pledge details
                    date_of_pledge=parse_date(request.form.get('date_of_pledge')),
                    time_of_pledge=parse_time(request.form.get('time_of_pledge')),
                    organs_consented=request.form.get('organs_consented'),
                    language_preference=selected_lang,
                    place_of_pledge=request.form.get('place'),
                    pledge_additional_notes=request.form.get('additional_notes'),
                    
                    # Witness 1
                    witness1_name=request.form.get('witness1_name'),
                    witness1_relationship=request.form.get('witness1_relationship'),
                    witness1_mobile=request.form.get('witness1_mobile'),
                    witness1_email=request.form.get('witness1_email'),
                    witness1_telephone=request.form.get('witness1_telephone'),
                    witness1_address=request.form.get('witness1_address'),
                    
                    # Witness 2
                    witness2_name=request.form.get('witness2_name'),
                    witness2_relationship=request.form.get('witness2_relationship'),
                    witness2_mobile=request.form.get('witness2_mobile'),
                    witness2_email=request.form.get('witness2_email'),
                    witness2_telephone=request.form.get('witness2_telephone'),
                    witness2_address=request.form.get('witness2_address'),
                    
                    # Consent
                    consent_given=True,
                    preferred_eye_bank=request.form.get('preferred_eye_bank'),
                    source='Online Form',
                )
                
                db.session.add(pledge)
                db.session.commit()
                
                app_logger.info(f"Pledge saved successfully. Reference: {ref_num}")
                flash('Pledge submitted successfully!', 'success')
                app_logger.info("Redirecting to success page")
                return redirect(url_for('success', ref_num=ref_num))
                
            except Exception as e:
                db.session.rollback()
                app_logger.error(f"Error saving pledge: {str(e)}", exc_info=True)
                flash(f'Error saving pledge: {str(e)}', 'danger')
                return safe_render('pledge_form.html', form_data=request.form)
        
        return safe_render('pledge_form.html', form_data={})

    @app.route("/success/<ref_num>")
    def success(ref_num):
        """Success page after pledge submission"""
        pledge = EyeDonationPledge.query.filter_by(reference_number=ref_num).first()
        return safe_render('success.html', pledge=pledge, ref_num=ref_num)

    @app.route("/pledge/<ref_num>/view")
    def view_pledge(ref_num):
        """View submitted pledge (public)"""
        pledge = EyeDonationPledge.query.filter_by(reference_number=ref_num).first_or_404()
        return safe_render('pledge_view.html', pledge=pledge)

    # ========================
    # ADMIN ROUTES
    # ========================
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        """Admin login"""
        if request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')
            
            admin = AdminUser.query.filter_by(username=username).first()
            
            if admin and check_password_hash(admin.password_hash, password):
                session['admin_user_id'] = admin.id
                session['admin_username'] = admin.username
                admin.last_login = datetime.utcnow()
                db.session.commit()
                
                log_security_event('LOGIN_SUCCESS', f"Admin user '{admin.username}' logged in", user_id=admin.id)
                
                flash(f'Welcome {admin.full_name}!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                log_security_event('LOGIN_FAILURE', f"Failed login attempt for username: {username}", level='warning')
                flash('Invalid username or password', 'danger')
        
        return safe_render('admin/login.html')

    @app.route("/admin/logout")
    def admin_logout():
        """Admin logout"""
        session.clear()
        flash('Logged out successfully', 'info')
        return redirect(url_for('index'))

    @app.route("/admin")
    @app.route("/admin/dashboard")
    @login_required
    def admin_dashboard():
        """Admin dashboard with statistics"""
        total_pledges = EyeDonationPledge.query.filter_by(is_active=True).count()
        # Get pledges by state (top 5)
        pledges_by_state = db.session.query(
            EyeDonationPledge.state,
            db.func.count(EyeDonationPledge.id).label('count')
        ).filter_by(is_active=True).group_by(EyeDonationPledge.state).order_by(
            db.func.count(EyeDonationPledge.id).desc()
        ).limit(5).all()
        
        # Get monthly statistics
        from sqlalchemy import extract
        monthly_stats = db.session.query(
            extract('month', EyeDonationPledge.created_at).label('month'),
            db.func.count(EyeDonationPledge.id).label('count')
        ).filter_by(is_active=True).filter(
            EyeDonationPledge.created_at >= datetime.now() - timedelta(days=365)
        ).group_by('month').all()
        
        return safe_render('admin/dashboard.html',
                             total_pledges=total_pledges,
                             pledges_by_state=pledges_by_state,
                             monthly_stats=monthly_stats)

    @app.route("/admin/pledges", methods=["GET"])
    @login_required
    def admin_pledges():
        """Admin pledges list with search and filter"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        state = request.args.get('state', '')
        
        query = EyeDonationPledge.query.filter_by(is_active=True)
        
        # Search
        if search:
            query = query.filter(
                (EyeDonationPledge.donor_name.ilike(f'%{search}%')) |
                (EyeDonationPledge.donor_mobile.ilike(f'%{search}%')) |
                (EyeDonationPledge.donor_email.ilike(f'%{search}%')) |
                (EyeDonationPledge.reference_number.ilike(f'%{search}%'))
            )
        
        # Filter by state
        if state:
            query = query.filter_by(state=state)
        
        # Pagination
        pledges = query.order_by(EyeDonationPledge.created_at.desc()).paginate(
            page=page,
            per_page=app.config.get('PLEDGES_PER_PAGE', 20)
        )
        
        return safe_render('admin/pledges_list.html',
                     pledges=pledges,
                     pagination=pledges,
                     search=search,
                     state=state)

    @app.route("/admin/pledge/<int:pledge_id>")
    @login_required
    def admin_pledge_detail(pledge_id):
        """Admin pledge detail view"""
        pledge = EyeDonationPledge.query.get_or_404(pledge_id)
        audit_logs = AuditLog.query.filter_by(pledge_id=pledge_id).order_by(
            AuditLog.created_at.desc()
        ).all()
        return safe_render('admin/pledge_detail.html', pledge=pledge, audit_logs=audit_logs)





    @app.route("/admin/export", methods=["GET"])
    @login_required
    def admin_export():
        """Export pledges as CSV"""
        search = request.args.get('search', '')
        state = request.args.get('state', '')
        
        query = EyeDonationPledge.query.filter_by(is_active=True)
        
        if search:
            query = query.filter(
                (EyeDonationPledge.donor_name.ilike(f'%{search}%')) |
                (EyeDonationPledge.donor_mobile.ilike(f'%{search}%'))
            )
        
        if state:
            query = query.filter_by(state=state)
        
        pledges = query.all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Reference Number', 'Donor Name', 'Mobile', 'Email', 'State', 
            'Created Date'
        ])
        
        for pledge in pledges:
            writer.writerow([
                pledge.reference_number,
                pledge.donor_name,
                pledge.donor_mobile,
                pledge.donor_email,
                pledge.state,
                pledge.created_at.strftime('%Y-%m-%d')
            ])
        
        # Log security event
        admin_id = session.get('admin_user_id')
        log_security_event('DATA_EXPORT', f"Exported {len(pledges)} pledges to CSV", user_id=admin_id)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=pledges_export.csv'
            }
        )

    @app.route("/admin/pledge/<int:pledge_id>/print")
    @login_required
    def admin_print_pledge(pledge_id):
        """Print/PDF view of pledge"""
        pledge = EyeDonationPledge.query.get_or_404(pledge_id)
        return safe_render('admin/pledge_print.html', pledge=pledge)

    # ========================
    # CLI Commands
    # ========================
    @app.cli.command()
    def init_db():
        """Initialize database"""
        db.create_all()
        print("Database initialized")

    @app.cli.command()
    def create_admin():
        """Create admin user"""
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        full_name = input("Enter full name: ")
        email = input("Enter email: ")
        
        admin = AdminUser(
            username=username,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            email=email,
            is_active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully")

    @app.cli.command()
    def delete_admin():
        """Delete admin user"""
        username = input("Enter admin username: ")
        admin = AdminUser.query.filter_by(username=username).first()
        if admin:
            db.session.delete(admin)
            db.session.commit()
            print(f"Admin user '{username}' deleted successfully")
        else:
            print(f"Admin user '{username}' not found")

    @app.cli.command()
    def reset_db():
        """Reset database (drop all tables)"""
        if input("Are you sure? (y/N): ").lower() == 'y':
            db.drop_all()
            db.create_all()
            print("Database reset successfully")

    # ========================
    # LOG ROUTES
    # ========================
    @app.route("/admin/logs")
    @login_required
    def admin_logs():
        """Superadmin log viewer"""
        # Filter params
        log_type = request.args.get('log_type')
        level = request.args.get('level')
        search = request.args.get('search')
        user_id = request.args.get('user_id')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        
        # Base query
        query = SystemLog.query.order_by(SystemLog.timestamp.desc())
        
        # Apply filters
        if log_type:
            query = query.filter_by(log_type=log_type)
        if level:
            query = query.filter_by(level=level)
        if user_id:
            query = query.filter_by(user_id=user_id)
        if search:
            query = query.filter(SystemLog.message.ilike(f'%{search}%'))
            
        # Date Filters
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                query = query.filter(SystemLog.timestamp >= start_date)
            except ValueError:
                pass # Ignore invalid dates
        
        if end_date_str:
            try:
                # Include the entire end date (up to 23:59:59)
                end_date_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
                end_date = end_date_dt + timedelta(days=1)
                query = query.filter(SystemLog.timestamp < end_date)
            except ValueError:
                pass
            
        # Pagination
        logs = query.paginate(page=page, per_page=20, error_out=False)
        
        # Get users for dropdown
        users = AdminUser.query.with_entities(AdminUser.id, AdminUser.username).all()
        
        return safe_render('admin/logs.html', 
                          logs=logs, 
                          active_page='logs',
                          users=users,
                          log_type=log_type, 
                          level=level, 
                          search=search,
                          user_id=int(user_id) if user_id else '',
                          start_date=start_date_str,
                          end_date=end_date_str)

    @app.route("/admin/logs/clear", methods=["POST"])
    @login_required
    def admin_clear_logs():
        """Clear all system logs"""
        try:
            # Delete all logs
            num_deleted = db.session.query(SystemLog).delete()
            db.session.commit()
            
            # Log this action
            admin_id = session.get('admin_user_id')
            log_security_event('LOGS_CLEARED', f"Cleared {num_deleted} system logs", user_id=admin_id, level='WARNING')
            
            flash(f'Successfully cleared {num_deleted} logs.', 'success')
        except Exception as e:
            db.session.rollback()
            error_logger.error(f"Failed to clear logs: {str(e)}")
            flash(f'Failed to clear logs: {str(e)}', 'danger')
            
        return redirect(url_for('admin_logs'))


    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
