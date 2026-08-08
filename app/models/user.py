from datetime import datetime
from flask_login import UserMixin
from extensions import db
from utils.security import hash_password, verify_password

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), default="user")  # 'admin' or 'user'
    avatar_url = db.Column(db.String(500), nullable=True)
    google_id = db.Column(db.String(100), nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    phone = db.Column(db.String(50), nullable=True)
    professional_title = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = db.relationship("Resume", backref="user", lazy=True, cascade="all, delete-orphan")
    reports = db.relationship("Report", backref="user", lazy=True, cascade="all, delete-orphan")
    criteria = db.relationship("Criteria", backref="user", lazy=True, cascade="all, delete-orphan")
    logs = db.relationship("AnalysisLog", backref="user", lazy=True, cascade="all, delete-orphan")
    settings = db.relationship("UserSettings", backref="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = hash_password(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return verify_password(password, self.password_hash)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "full_name": self.name,
            "role": self.role,
            "avatar_url": self.avatar_url or f"https://api.dicebear.com/7.x/initials/svg?seed={self.name}",
            "phone": self.phone or "",
            "professional_title": self.professional_title or "Talent Acquisition / Candidate",
            "location": self.location or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
