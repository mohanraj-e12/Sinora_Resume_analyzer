import json
from datetime import datetime
from extensions import db

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Extracted metadata fields
    candidate_name = db.Column(db.String(150), nullable=True)
    candidate_email = db.Column(db.String(120), nullable=True)
    candidate_phone = db.Column(db.String(50), nullable=True)
    candidate_address = db.Column(db.String(255), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    github = db.Column(db.String(255), nullable=True)
    portfolio = db.Column(db.String(255), nullable=True)
    
    # JSON strings for structured extracted data
    education_json = db.Column(db.Text, default="[]")
    experience_json = db.Column(db.Text, default="[]")
    projects_json = db.Column(db.Text, default="[]")
    skills_json = db.Column(db.Text, default="[]")
    certifications_json = db.Column(db.Text, default="[]")
    languages_json = db.Column(db.Text, default="[]")
    achievements_json = db.Column(db.Text, default="[]")
    internships_json = db.Column(db.Text, default="[]")
    publications_json = db.Column(db.Text, default="[]")
    soft_skills_json = db.Column(db.Text, default="[]")
    technical_skills_json = db.Column(db.Text, default="[]")
    
    raw_text = db.Column(db.Text, nullable=True)

    # Relationships
    report = db.relationship("Report", backref="resume", uselist=False, cascade="all, delete-orphan")

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
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "candidate_name": self.candidate_name or "Unknown Candidate",
            "candidate_email": self.candidate_email,
            "candidate_phone": self.candidate_phone,
            "linkedin": self.linkedin,
            "github": self.github,
            "portfolio": self.portfolio,
            "education": self.get_data("education_json"),
            "experience": self.get_data("experience_json"),
            "projects": self.get_data("projects_json"),
            "skills": self.get_data("skills_json"),
            "technical_skills": self.get_data("technical_skills_json"),
            "soft_skills": self.get_data("soft_skills_json"),
            "certifications": self.get_data("certifications_json"),
            "languages": self.get_data("languages_json"),
            "achievements": self.get_data("achievements_json"),
            "internships": self.get_data("internships_json"),
            "publications": self.get_data("publications_json"),
        }
