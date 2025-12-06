from datetime import datetime, timedelta
from functools import wraps
import os
import csv
from io import StringIO

from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import EyeDonationPledge, AdminUser, AuditLog, db

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

    # ========================
    # Error Handlers
    # ========================
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('500.html'), 500

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
        if not form_data.get('donor_mobile'):
            errors.append('Mobile number is required')
        if not form_data.get('donor_email'):
            errors.append('Email is required')
        if not form_data.get('witness1_name'):
            errors.append('Witness 1 name is required')
        if not form_data.get('consent'):
            errors.append('Consent must be given')
        
        # Email validation
        if form_data.get('donor_email') and '@' not in form_data.get('donor_email', ''):
            errors.append('Invalid email address')
        
        # Mobile validation
        if form_data.get('donor_mobile') and not form_data.get('donor_mobile').isdigit():
            errors.append('Mobile number must contain only digits')
        
        return errors

    # ========================
    # PUBLIC ROUTES
    # ========================
    @app.route("/")
    def index():
        """Home page"""
        return render_template('index.html')

    @app.route("/pledge", methods=["GET", "POST"])
    def pledge_form():
        """Pledge form - display and submit"""
        if request.method == "POST":
            # Validate
            errors = validate_pledge(request.form)
            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('pledge_form.html', form_data=request.form)
            
            try:
                # Generate reference number
                ref_num = generate_reference_number()
                
                # Create pledge
                pledge = EyeDonationPledge(
                    reference_number=ref_num,
                    donor_name=request.form.get('donor_name'),
                    donor_gender=request.form.get('donor_gender'),
                    donor_dob=parse_date(request.form.get('donor_dob')),
                    donor_age=int(request.form.get('donor_age') or 0),
                    donor_blood_group=request.form.get('donor_blood_group'),
                    donor_mobile=request.form.get('donor_mobile'),
                    donor_email=request.form.get('donor_email'),
                    donor_marital_status=request.form.get('donor_marital_status'),
                    donor_occupation=request.form.get('donor_occupation'),
                    donor_id_proof_type=request.form.get('donor_id_proof_type'),
                    donor_id_proof_number=request.form.get('donor_id_proof_number'),
                    
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
                    language_preference=request.form.get('language_preference'),
                    place_of_pledge=request.form.get('place_of_pledge'),
                    pledge_additional_notes=request.form.get('pledge_additional_notes'),
                    
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
                
                flash('Pledge submitted successfully!', 'success')
                return redirect(url_for('success', ref_num=ref_num))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error saving pledge: {str(e)}', 'danger')
                return render_template('pledge_form.html', form_data=request.form)
        
        return render_template('pledge_form.html', form_data={})

    @app.route("/success/<ref_num>")
    def success(ref_num):
        """Success page after pledge submission"""
        pledge = EyeDonationPledge.query.filter_by(reference_number=ref_num).first()
        return render_template('success.html', pledge=pledge, ref_num=ref_num)

    @app.route("/pledge/<ref_num>/view")
    def view_pledge(ref_num):
        """View submitted pledge (public)"""
        pledge = EyeDonationPledge.query.filter_by(reference_number=ref_num).first_or_404()
        return render_template('pledge_view.html', pledge=pledge)

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
                flash(f'Welcome {admin.full_name}!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        
        return render_template('admin/login.html')

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
        verified_pledges = EyeDonationPledge.query.filter_by(is_active=True, is_verified=True).count()
        pending_pledges = total_pledges - verified_pledges
        
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
        
        return render_template('admin/dashboard.html',
                             total_pledges=total_pledges,
                             verified_pledges=verified_pledges,
                             pending_pledges=pending_pledges,
                             pledges_by_state=pledges_by_state,
                             monthly_stats=monthly_stats)

    @app.route("/admin/pledges", methods=["GET"])
    @login_required
    def admin_pledges():
        """Admin pledges list with search and filter"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
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
        
        # Filter by status
        if status == 'verified':
            query = query.filter_by(is_verified=True)
        elif status == 'pending':
            query = query.filter_by(is_verified=False)
        
        # Filter by state
        if state:
            query = query.filter_by(state=state)
        
        # Pagination
        pledges = query.order_by(EyeDonationPledge.created_at.desc()).paginate(
            page=page,
            per_page=app.config.get('PLEDGES_PER_PAGE', 20)
        )
        
        return render_template('admin/pledges_list.html',
                             pledges=pledges,
                             search=search,
                             status=status,
                             state=state)

    @app.route("/admin/pledge/<int:pledge_id>")
    @login_required
    def admin_pledge_detail(pledge_id):
        """Admin pledge detail view"""
        pledge = EyeDonationPledge.query.get_or_404(pledge_id)
        audit_logs = AuditLog.query.filter_by(pledge_id=pledge_id).order_by(
            AuditLog.created_at.desc()
        ).all()
        return render_template('admin/pledge_detail.html', pledge=pledge, audit_logs=audit_logs)

    @app.route("/admin/pledge/<int:pledge_id>/verify", methods=["POST"])
    @login_required
    def admin_verify_pledge(pledge_id):
        """Mark pledge as verified"""
        pledge = EyeDonationPledge.query.get_or_404(pledge_id)
        admin_id = session.get('admin_user_id')
        
        pledge.is_verified = True
        pledge.verified_at = datetime.utcnow()
        pledge.verified_by = admin_id
        
        # Log audit
        audit_log = AuditLog(
            admin_user_id=admin_id,
            pledge_id=pledge_id,
            action='VERIFIED',
            details='Pledge marked as verified'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        flash('Pledge marked as verified', 'success')
        return redirect(url_for('admin_pledge_detail', pledge_id=pledge_id))

    @app.route("/admin/pledge/<int:pledge_id>/unverify", methods=["POST"])
    @login_required
    def admin_unverify_pledge(pledge_id):
        """Mark pledge as unverified"""
        pledge = EyeDonationPledge.query.get_or_404(pledge_id)
        admin_id = session.get('admin_user_id')
        
        pledge.is_verified = False
        pledge.verified_at = None
        pledge.verified_by = None
        
        # Log audit
        audit_log = AuditLog(
            admin_user_id=admin_id,
            pledge_id=pledge_id,
            action='UNVERIFIED',
            details='Pledge marked as unverified'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        flash('Pledge marked as unverified', 'info')
        return redirect(url_for('admin_pledge_detail', pledge_id=pledge_id))

    @app.route("/admin/pledge/<int:pledge_id>/deactivate", methods=["POST"])
    @login_required
    def admin_deactivate_pledge(pledge_id):
        """Deactivate pledge (soft delete)"""
        pledge = EyeDonationPledge.query.get_or_404(pledge_id)
        admin_id = session.get('admin_user_id')
        
        pledge.is_active = False
        
        # Log audit
        audit_log = AuditLog(
            admin_user_id=admin_id,
            pledge_id=pledge_id,
            action='DEACTIVATED',
            details='Pledge deactivated'
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        flash('Pledge deactivated', 'warning')
        return redirect(url_for('admin_pledges'))

    @app.route("/admin/export", methods=["GET"])
    @login_required
    def admin_export():
        """Export pledges as CSV"""
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        state = request.args.get('state', '')
        
        query = EyeDonationPledge.query.filter_by(is_active=True)
        
        if search:
            query = query.filter(
                (EyeDonationPledge.donor_name.ilike(f'%{search}%')) |
                (EyeDonationPledge.donor_mobile.ilike(f'%{search}%'))
            )
        
        if status == 'verified':
            query = query.filter_by(is_verified=True)
        elif status == 'pending':
            query = query.filter_by(is_verified=False)
        
        if state:
            query = query.filter_by(state=state)
        
        pledges = query.all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Reference Number', 'Donor Name', 'Mobile', 'Email', 'State', 
            'Status', 'Created Date', 'Verified Date'
        ])
        
        for pledge in pledges:
            writer.writerow([
                pledge.reference_number,
                pledge.donor_name,
                pledge.donor_mobile,
                pledge.donor_email,
                pledge.state,
                'Verified' if pledge.is_verified else 'Pending',
                pledge.created_at.strftime('%Y-%m-%d'),
                pledge.verified_at.strftime('%Y-%m-%d') if pledge.verified_at else ''
            ])
        
        # Log audit
        admin_id = session.get('admin_user_id')
        audit_log = AuditLog(
            admin_user_id=admin_id,
            action='EXPORT',
            details=f'Exported {len(pledges)} pledges to CSV'
        )
        db.session.add(audit_log)
        db.session.commit()
        
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
        return render_template('admin/pledge_print.html', pledge=pledge)

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
    def reset_db():
        """Reset database (drop all tables)"""
        if input("Are you sure? (y/N): ").lower() == 'y':
            db.drop_all()
            db.create_all()
            print("Database reset successfully")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
