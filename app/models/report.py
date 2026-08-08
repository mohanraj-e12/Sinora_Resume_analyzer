import json
from datetime import datetime
from extensions import db

class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Calculated ATS metrics
    ats_score = db.Column(db.Float, default=0.0)
    selection_percentage = db.Column(db.Float, default=0.0)
    skill_match = db.Column(db.Float, default=0.0)
    keyword_match = db.Column(db.Float, default=0.0)
    education_match = db.Column(db.Float, default=0.0)
    experience_match = db.Column(db.Float, default=0.0)
    completeness_score = db.Column(db.Float, default=0.0)
    formatting_score = db.Column(db.Float, default=0.0)
    grammar_score = db.Column(db.Float, default=0.0)
    readability_score = db.Column(db.Float, default=0.0)
    overall_quality = db.Column(db.String(50), default="Good")

    # JSON lists
    missing_skills_json = db.Column(db.Text, default="[]")
    missing_keywords_json = db.Column(db.Text, default="[]")
    duplicate_skills_json = db.Column(db.Text, default="[]")
    recommendations_json = db.Column(db.Text, default="[]")
    keyword_coverage_json = db.Column(db.Text, default="{}")

    # AI Analysis Output from Gemini API
    professional_summary = db.Column(db.Text, nullable=True)
    strengths_json = db.Column(db.Text, default="[]")
    weaknesses_json = db.Column(db.Text, default="[]")
    resume_review = db.Column(db.Text, nullable=True)
    hr_review = db.Column(db.Text, nullable=True)
    improvement_suggestions_json = db.Column(db.Text, default="[]")
    interview_readiness_json = db.Column(db.Text, default="{}")
    optimization_tips_json = db.Column(db.Text, default="[]")
    career_suggestions_json = db.Column(db.Text, default="[]")
    job_recommendations_json = db.Column(db.Text, default="[]")
    score_explanations_json = db.Column(db.Text, default="{}")

    pdf_report_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_data(self, field_name):
        val = getattr(self, field_name, "[]")
        try:
            return json.loads(val) if val else ([] if field_name.endswith("_json") and not isinstance(json.loads(val), dict) else {})
        except Exception:
            return [] if "list" in field_name or field_name.endswith("s_json") else {}

    def set_data(self, field_name, value):
        setattr(self, field_name, json.dumps(value))

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "user_id": self.user_id,
            "ats_score": round(self.ats_score, 1),
            "selection_percentage": round(self.selection_percentage, 1),
            "skill_match": round(self.skill_match, 1),
            "keyword_match": round(self.keyword_match, 1),
            "education_match": round(self.education_match, 1),
            "experience_match": round(self.experience_match, 1),
            "completeness_score": round(self.completeness_score, 1),
            "formatting_score": round(self.formatting_score, 1),
            "grammar_score": round(self.grammar_score, 1),
            "readability_score": round(self.readability_score, 1),
            "overall_quality": self.overall_quality,
            "missing_skills": self.get_data("missing_skills_json"),
            "missing_keywords": self.get_data("missing_keywords_json"),
            "duplicate_skills": self.get_data("duplicate_skills_json"),
            "recommendations": self.get_data("recommendations_json"),
            "keyword_coverage": self.get_data("keyword_coverage_json"),
            "professional_summary": self.professional_summary,
            "strengths": self.get_data("strengths_json"),
            "weaknesses": self.get_data("weaknesses_json"),
            "resume_review": self.resume_review,
            "hr_review": self.hr_review,
            "improvement_suggestions": self.get_data("improvement_suggestions_json"),
            "interview_readiness": self.get_data("interview_readiness_json"),
            "optimization_tips": self.get_data("optimization_tips_json"),
            "career_suggestions": self.get_data("career_suggestions_json"),
            "job_recommendations": self.get_data("job_recommendations_json"),
            "score_explanations": self.get_data("score_explanations_json"),
            "pdf_report_path": self.pdf_report_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
