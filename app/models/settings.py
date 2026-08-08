import json
from datetime import datetime
from extensions import db

class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    theme = db.Column(db.String(20), default="light")
    language = db.Column(db.String(20), default="en")
    
    email_notifications = db.Column(db.Boolean, default=True)
    analysis_notifications = db.Column(db.Boolean, default=True)
    account_notifications = db.Column(db.Boolean, default=True)
    product_updates = db.Column(db.Boolean, default=False)
    
    default_target_role = db.Column(db.String(150), nullable=True, default="Senior Software Engineer")
    default_required_skills = db.Column(db.Text, default="[]")
    default_preferred_skills = db.Column(db.Text, default="[]")
    experience_level = db.Column(db.String(50), nullable=True, default="Mid-Senior (3-5 years)")
    education_requirement = db.Column(db.String(100), nullable=True, default="Bachelor's Degree")
    certifications = db.Column(db.Text, default="[]")
    custom_requirements = db.Column(db.Text, nullable=True)
    
    ats_preferences_json = db.Column(db.Text, default='{"keyword_weight": 25, "skills_weight": 35, "formatting_check": true, "structure_check": true}')
    privacy_preferences_json = db.Column(db.Text, default='{"store_resumes": true, "store_history": true, "data_usage": "analytics"}')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_data(self, field_name):
        val = getattr(self, field_name, "[]")
        try:
            return json.loads(val) if val else []
        except Exception:
            return []

    def set_data(self, field_name, value):
        setattr(self, field_name, json.dumps(value))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "theme": self.theme or "light",
            "language": self.language or "en",
            "email_notifications": self.email_notifications,
            "analysis_notifications": self.analysis_notifications,
            "account_notifications": self.account_notifications,
            "product_updates": self.product_updates,
            "default_target_role": self.default_target_role or "",
            "default_required_skills": self.get_data("default_required_skills"),
            "default_preferred_skills": self.get_data("default_preferred_skills"),
            "experience_level": self.experience_level or "",
            "education_requirement": self.education_requirement or "",
            "certifications": self.get_data("certifications"),
            "custom_requirements": self.custom_requirements or "",
            "ats_preferences": self.get_data("ats_preferences_json"),
            "privacy_preferences": self.get_data("privacy_preferences_json"),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
