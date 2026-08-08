from datetime import datetime
from extensions import db

class AnalysisLog(db.Model):
    __tablename__ = "analysis_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    log_type = db.Column(db.String(20), default="INFO")  # INFO, DEBUG, WARN, ERROR, PROCESSING
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "resume_id": self.resume_id,
            "action": self.action,
            "message": self.message,
            "log_type": self.log_type,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None,
        }
