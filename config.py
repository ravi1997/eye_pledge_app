import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration"""
    
    # =====================
    # Database
    # =====================
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "sqlite:///" + os.path.join(basedir, "pledge.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # =====================
    # Security & Session
    # =====================
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # =====================
    # Flask Settings
    # =====================
    DEBUG = False
    TESTING = False
    PROPAGATE_EXCEPTIONS = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # =====================
    # Institution Information
    # =====================
    INSTITUTION_NAME = os.environ.get("INSTITUTION_NAME", "National Eye Bank")
    INSTITUTION_ADDRESS = os.environ.get(
        "INSTITUTION_ADDRESS",
        "Medical Campus, City"
    )
    INSTITUTION_EMAIL = os.environ.get("INSTITUTION_EMAIL", "info@eyebank.org")
    INSTITUTION_PHONE = os.environ.get("INSTITUTION_PHONE", "+91-1234567890")
    INSTITUTION_WEBSITE = os.environ.get("INSTITUTION_WEBSITE", "https://eyebank.org")
    
    # =====================
    # Admin Settings
    # =====================
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@eyebank.org")
    
    # =====================
    # Pagination
    # =====================
    PLEDGES_PER_PAGE = int(os.environ.get("PLEDGES_PER_PAGE", 20))
    AUDIT_LOGS_PER_PAGE = int(os.environ.get("AUDIT_LOGS_PER_PAGE", 50))
    
    # =====================
    # Email Settings (for future use)
    # =====================
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", True)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@eyebank.org")
    
    # =====================
    # Form Settings
    # =====================
    DEFAULT_CONSENT_TEXT = """
    I hereby declare that I wish to donate my eyes after my death to help the blind 
    and restore sight. I understand that this is a voluntary act and can be revoked 
    at any time. The eye bank will use my eyes for corneal transplantation, research, 
    or medical education as per the prevailing guidelines and my consent.
    """
    
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    # =====================
    # API Settings (for future use)
    # =====================
    API_TITLE = "Eye Donation Pledge API"
    API_VERSION = "1.0.0"
    
    # =====================
    # Feature Flags
    # =====================
    ENABLE_EMAIL_VERIFICATION = False
    ENABLE_OTP_VERIFICATION = False
    ENABLE_DIGITAL_SIGNATURE = False
    ENABLE_API = False
    ENABLE_EXPORT = True
    ENABLE_PRINT = True


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = os.environ.get("SECRET_KEY")
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")

