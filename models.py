"""
Database models for Eye Donation Pledge Form system.
Designed to work with SQLite locally and PostgreSQL in production.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
import uuid

db = SQLAlchemy()


class GenderEnum(Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "Prefer not to say"


class MaritalStatusEnum(Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"
    OTHER = "Other"


class IdProofTypeEnum(Enum):
    AADHAAR = "Aadhaar"
    PAN = "PAN"
    VOTER_ID = "Voter ID"
    PASSPORT = "Passport"
    DRIVING_LICENSE = "Driving License"
    OTHER = "Other"


class OrgansConsentsEnum(Enum):
    CORNEA_ONLY = "Cornea only"
    WHOLE_EYE = "Whole eye"
    BOTH_EYES = "Both eyes"
    SCLERA = "Sclera"
    OTHER = "Other"


class SourceEnum(Enum):
    SELF = "self"
    CAMP = "camp"
    HOSPITAL_DESK = "hospital desk"
    WEBSITE = "website"
    PHONE = "phone"
    MAIL = "mail"
    OTHER = "other"


class EyeDonationPledge(db.Model):
    """
    Main model for storing eye donation pledges.
    Captures donor info, consent, witnesses, and admin metadata.
    """
    __tablename__ = 'eye_donation_pledges'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Unique reference number (e.g., NEB-2025-000001)
    reference_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(100), nullable=True)
    source = db.Column(db.String(20), default=SourceEnum.WEBSITE.value, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by = db.Column(db.String(100), nullable=True)

    # ===== A. DONOR DETAILS =====
    donor_name = db.Column(db.String(150), nullable=False, index=True)
    gender = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    age = db.Column(db.Integer, nullable=True)  # Can be calculated or provided
    blood_group = db.Column(db.String(5), nullable=True)  # A, B, O, AB with +/-
    donor_mobile = db.Column(db.String(20), nullable=True, index=True)
    donor_email = db.Column(db.String(100), nullable=True)
    relation = db.Column(db.String(50), nullable=True)  # "son of", "daughter of", etc.
    relative_name = db.Column(db.String(150), nullable=True)
    marital_status = db.Column(db.String(20), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    id_proof_type = db.Column(db.String(30), nullable=True)
    id_proof_number = db.Column(db.String(50), nullable=True)

    # ===== B. ADDRESS DETAILS =====
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    district = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=False, index=True)
    pincode = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(100), default="India", nullable=False)

    # ===== C. PLEDGE / CONSENT DETAILS =====
    place = db.Column(db.String(255), nullable=True)
    date_of_pledge = db.Column(db.Date, nullable=False, index=True)
    time_of_pledge = db.Column(db.Time, nullable=True)
    
    # Consent text - stores the specific version this donor consented to
    consent_text = db.Column(db.Text, nullable=True)
    
    # Organs consented - can store comma-separated or JSON in future
    organs_consented = db.Column(db.String(255), default="Both eyes", nullable=False)
    
    # Language of consent
    language_of_consent = db.Column(db.String(50), default="English", nullable=False)
    
    # Consent acknowledgment
    is_consent_revocable = db.Column(db.Boolean, default=True, nullable=False)
    donor_acknowledged_revocability = db.Column(db.Boolean, default=False, nullable=True)
    
    # Preferred eye bank
    preferred_eye_bank = db.Column(db.String(255), nullable=True)
    
    # Additional notes
    additional_notes = db.Column(db.Text, nullable=True)

    # ===== D. WITNESS 1 (Next of Kin - Mandatory) =====
    witness1_name = db.Column(db.String(150), nullable=False, index=True)
    witness1_relationship = db.Column(db.String(50), nullable=True)
    witness1_address = db.Column(db.Text, nullable=True)
    witness1_mobile = db.Column(db.String(20), nullable=True)
    witness1_telephone = db.Column(db.String(20), nullable=True)
    witness1_email = db.Column(db.String(100), nullable=True)
    witness1_is_next_of_kin = db.Column(db.Boolean, default=True, nullable=False)

    # ===== E. WITNESS 2 (Optional) =====
    witness2_name = db.Column(db.String(150), nullable=True)
    witness2_relationship = db.Column(db.String(50), nullable=True)
    witness2_address = db.Column(db.Text, nullable=True)
    witness2_mobile = db.Column(db.String(20), nullable=True)
    witness2_telephone = db.Column(db.String(20), nullable=True)
    witness2_email = db.Column(db.String(100), nullable=True)

    # ===== DIGITAL CONSENT (Future: Digital Signature) =====
    # Placeholder for digital signature / consent capture
    donor_consent_checkbox = db.Column(db.Boolean, default=False, nullable=False)
    donor_consent_datetime = db.Column(db.DateTime, nullable=True)
    witness1_consent_checkbox = db.Column(db.Boolean, default=False, nullable=True)
    witness1_consent_datetime = db.Column(db.DateTime, nullable=True)
    
    # Future: OTP verification status
    donor_mobile_verified = db.Column(db.Boolean, default=False, nullable=False)
    donor_mobile_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Future: Email confirmation
    donor_email_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    donor_email_confirmed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<EyeDonationPledge {self.reference_number} - {self.donor_name}>"

    def to_dict(self):
        """Convert model to dictionary for JSON export."""
        return {
            'reference_number': self.reference_number,
            'donor_name': self.donor_name,
            'donor_email': self.donor_email,
            'donor_mobile': self.donor_mobile,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'blood_group': self.blood_group,
            'gender': self.gender,
            'marital_status': self.marital_status,
            'occupation': self.occupation,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'district': self.district,
            'state': self.state,
            'pincode': self.pincode,
            'country': self.country,
            'place': self.place,
            'date_of_pledge': self.date_of_pledge.isoformat() if self.date_of_pledge else None,
            'time_of_pledge': self.time_of_pledge.isoformat() if self.time_of_pledge else None,
            'organs_consented': self.organs_consented,
            'language_of_consent': self.language_of_consent,
            'preferred_eye_bank': self.preferred_eye_bank,
            'witness1_name': self.witness1_name,
            'witness1_relationship': self.witness1_relationship,
            'witness1_mobile': self.witness1_mobile,
            'witness1_email': self.witness1_email,
            'witness2_name': self.witness2_name,
            'witness2_mobile': self.witness2_mobile,
            'is_verified': self.is_verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'created_at': self.created_at.isoformat(),
        }


class AdminUser(db.Model):
    """
    Simple admin user model for authentication.
    In production, consider using Flask-Login or an auth service.
    """
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<AdminUser {self.username}>"


class AuditLog(db.Model):
    """
    Audit log for tracking important admin actions.
    Useful for compliance and debugging.
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    pledge_id = db.Column(db.Integer, db.ForeignKey('eye_donation_pledges.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # e.g., "verified", "exported", "edited"
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AuditLog {self.action} by user_id={self.admin_user_id}>"
