from flask import Blueprint, jsonify, request
from extensions import db
from models.user import User
from models.resume import Resume
from models.report import Report
from models.log import AnalysisLog

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/api/admin/dashboard", methods=["GET"])
def admin_dashboard():
    total_users = User.query.count()
    total_resumes = Resume.query.count()
    total_reports = Report.query.count()
    
    reports = Report.query.all()
    avg_ats_score = round(sum(r.ats_score for r in reports) / (len(reports) or 1), 1)
    
    logs = AnalysisLog.query.order_by(AnalysisLog.timestamp.desc()).limit(20).all()
    recent_resumes = Resume.query.order_by(Resume.upload_date.desc()).limit(10).all()

    return jsonify({
        "success": True,
        "stats": {
            "total_users": total_users,
            "total_resumes": total_resumes,
            "total_reports": total_reports,
            "avg_ats_score": avg_ats_score,
            "system_load": "75%",
            "storage_usage": "38%"
        },
        "recent_analyses": [
            {
                "resume": r.to_dict(),
                "report": r.report.to_dict() if r.report else None
            } for r in recent_resumes
        ],
        "logs": [l.to_dict() for l in logs]
    })

@admin_bp.route("/api/admin/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify({"success": True, "users": [u.to_dict() for u in users]})

@admin_bp.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": True, "message": f"User {user.email} deleted."})

@admin_bp.route("/api/admin/reports/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return jsonify({"success": True, "message": "Report deleted."})
