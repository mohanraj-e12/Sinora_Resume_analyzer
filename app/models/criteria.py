import json
from datetime import datetime
from extensions import db

class Criteria(db.Model):
    __tablename__ = "criteria"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    job_role = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(150), nullable=True)
    location = db.Column(db.String(150), nullable=True)
    
    required_skills_json = db.Column(db.Text, default="[]")
    preferred_skills_json = db.Column(db.Text, default="[]")
    min_experience = db.Column(db.Float, default=0.0)
    min_degree = db.Column(db.String(100), default="Bachelor's")
    branch = db.Column(db.String(100), nullable=True)
    certifications_json = db.Column(db.Text, default="[]")
    projects_json = db.Column(db.Text, default="[]")
    keywords_json = db.Column(db.Text, default="[]")
    languages_json = db.Column(db.Text, default="[]")
    custom_questions_json = db.Column(db.Text, default="[]")
    
    # Custom weights (0 to 100)
    skill_weight = db.Column(db.Float, default=30.0)
    experience_weight = db.Column(db.Float, default=25.0)
    education_weight = db.Column(db.Float, default=15.0)
    certification_weight = db.Column(db.Float, default=15.0)
    keyword_weight = db.Column(db.Float, default=15.0)
    
    is_template = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
            "title": self.title,
            "job_role": self.job_role,
            "industry": self.industry,
            "location": self.location,
            "required_skills": self.get_data("required_skills_json"),
            "preferred_skills": self.get_data("preferred_skills_json"),
            "min_experience": self.min_experience,
            "min_degree": self.min_degree,
            "branch": self.branch,
            "certifications": self.get_data("certifications_json"),
            "projects": self.get_data("projects_json"),
            "keywords": self.get_data("keywords_json"),
            "languages": self.get_data("languages_json"),
            "custom_questions": self.get_data("custom_questions_json"),
            "skill_weight": self.skill_weight,
            "experience_weight": self.experience_weight,
            "education_weight": self.education_weight,
            "certification_weight": self.certification_weight,
            "keyword_weight": self.keyword_weight,
            "is_template": self.is_template,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
