import os
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user, logout_user
from extensions import db
from models.user import User
from models.settings import UserSettings
from models.resume import Resume
from models.report import Report
from models.criteria import Criteria
from models.log import AnalysisLog

settings_bp = Blueprint("settings", __name__)

def get_or_create_settings(user_id):
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.session.add(settings)
        db.session.commit()
    return settings

def get_current_active_user():
    if current_user and current_user.is_authenticated:
        return current_user
    # Fallback to default first user or create one if db is empty
    user = User.query.first()
    if user:
        return user

    existing = User.query.filter_by(email="user@sinora.ai").first()
    if existing:
        return existing

    try:
        user = User(email="user@sinora.ai", name="Sinora User", role="user")
        user.set_password("SinoraSecure2026!")
        db.session.add(user)
        db.session.commit()
        return user
    except Exception:
        db.session.rollback()
        return User.query.filter_by(email="user@sinora.ai").first() or User.query.first()

@settings_bp.route("/api/user/profile", methods=["GET", "POST"])
def user_profile():
    user = get_current_active_user()
    if request.method == "POST":
        data = request.get_json() or request.form
        full_name = data.get("full_name") or data.get("name")
        if full_name and full_name.strip():
            user.name = full_name.strip()
        
        if "phone" in data:
            user.phone = data.get("phone", "").strip()
        if "professional_title" in data:
            user.professional_title = data.get("professional_title", "").strip()
        if "location" in data:
            user.location = data.get("location", "").strip()
        if "avatar_url" in data and data.get("avatar_url"):
            user.avatar_url = data.get("avatar_url").strip()
            
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Profile updated successfully.",
            "user": user.to_dict()
        })

    # Stats for Data & Storage
    resume_count = Resume.query.filter_by(user_id=user.id).count()
    report_count = Report.query.filter_by(user_id=user.id).count()
    criteria_count = Criteria.query.filter_by(user_id=user.id).count()

    return jsonify({
        "success": True,
        "user": user.to_dict(),
        "stats": {
            "uploaded_resumes": resume_count,
            "analysis_reports": report_count,
            "criteria_count": criteria_count
        }
    })

@settings_bp.route("/api/user/settings", methods=["GET", "POST"])
def user_settings():
    user = get_current_active_user()
    settings = get_or_create_settings(user.id)

    if request.method == "POST":
        data = request.get_json() or {}
        
        if "theme" in data:
            settings.theme = data["theme"]
        if "language" in data:
            settings.language = data["language"]
            
        if "email_notifications" in data:
            settings.email_notifications = bool(data["email_notifications"])
        if "analysis_notifications" in data:
            settings.analysis_notifications = bool(data["analysis_notifications"])
        if "account_notifications" in data:
            settings.account_notifications = bool(data["account_notifications"])
        if "product_updates" in data:
            settings.product_updates = bool(data["product_updates"])
            
        if "default_target_role" in data:
            settings.default_target_role = data["default_target_role"]
        if "default_required_skills" in data:
            settings.set_data("default_required_skills", data["default_required_skills"])
        if "default_preferred_skills" in data:
            settings.set_data("default_preferred_skills", data["default_preferred_skills"])
        if "experience_level" in data:
            settings.experience_level = data["experience_level"]
        if "education_requirement" in data:
            settings.education_requirement = data["education_requirement"]
        if "certifications" in data:
            settings.set_data("certifications", data["certifications"])
        if "custom_requirements" in data:
            settings.custom_requirements = data["custom_requirements"]
            
        if "ats_preferences" in data:
            settings.set_data("ats_preferences_json", data["ats_preferences"])
        if "privacy_preferences" in data:
            settings.set_data("privacy_preferences_json", data["privacy_preferences"])

        settings.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Settings saved successfully.",
            "settings": settings.to_dict()
        })

    return jsonify({
        "success": True,
        "settings": settings.to_dict()
    })

@settings_bp.route("/api/user/change-password", methods=["POST"])
def change_password():
    user = get_current_active_user()
    data = request.get_json() or {}
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if new_password != confirm_password:
        return jsonify({"success": False, "message": "New password and confirmation do not match."}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "New password must be at least 6 characters."}), 400

    if user.password_hash and not user.check_password(current_password):
        return jsonify({"success": False, "message": "Incorrect current password."}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"success": True, "message": "Password updated successfully."})

@settings_bp.route("/api/user/clear-resumes", methods=["POST"])
def clear_resumes():
    user = get_current_active_user()
    resumes = Resume.query.filter_by(user_id=user.id).all()
    count = len(resumes)
    for r in resumes:
        if r.file_path and os.path.exists(r.file_path):
            try:
                os.remove(r.file_path)
            except Exception:
                pass
        db.session.delete(r)
    db.session.commit()
    return jsonify({"success": True, "message": f"Successfully deleted {count} stored resumes."})

@settings_bp.route("/api/user/clear-history", methods=["POST"])
def clear_history():
    user = get_current_active_user()
    reports = Report.query.filter_by(user_id=user.id).all()
    logs = AnalysisLog.query.filter_by(user_id=user.id).all()
    r_count = len(reports)
    l_count = len(logs)
    
    for r in reports:
        db.session.delete(r)
    for l in logs:
        db.session.delete(l)
        
    db.session.commit()
    return jsonify({"success": True, "message": f"Successfully cleared {r_count} analysis reports and {l_count} logs."})

@settings_bp.route("/api/user/delete-account", methods=["POST"])
def delete_account():
    user = get_current_active_user()
    data = request.get_json() or {}
    confirm = data.get("confirm")
    if not confirm or confirm != "DELETE":
        return jsonify({"success": False, "message": "Confirmation required."}), 400

    db.session.delete(user)
    db.session.commit()
    logout_user()
    return jsonify({"success": True, "message": "Account deleted permanently."})
