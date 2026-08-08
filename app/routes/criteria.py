from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.criteria import Criteria

criteria_bp = Blueprint("criteria", __name__)

from routes.settings import get_current_active_user

def get_user_id():
    if current_user and current_user.is_authenticated:
        return current_user.id
    active_user = get_current_active_user()
    return active_user.id if active_user else 1

@criteria_bp.route("/api/criteria", methods=["GET"])
def get_criteria():
    user_id = get_user_id()
    criteria_list = Criteria.query.filter((Criteria.user_id == user_id) | (Criteria.is_template == True)).all()
    return jsonify({
        "success": True,
        "criteria": [c.to_dict() for c in criteria_list]
    })

@criteria_bp.route("/api/criteria/<int:criteria_id>", methods=["GET"])
def get_single_criteria(criteria_id):
    criteria = Criteria.query.get_or_404(criteria_id)
    return jsonify({"success": True, "criteria": criteria.to_dict()})

@criteria_bp.route("/api/criteria", methods=["POST"])
def create_criteria():
    data = request.get_json() or request.form
    user_id = get_user_id()

    title = data.get("title", "Custom Criteria")
    job_role = data.get("job_role", "Software Engineer")
    industry = data.get("industry", "Technology")
    location = data.get("location", "Remote")
    
    req_skills = data.get("required_skills", [])
    if isinstance(req_skills, str):
        req_skills = [s.strip() for s in req_skills.split(",") if s.strip()]

    pref_skills = data.get("preferred_skills", [])
    if isinstance(pref_skills, str):
        pref_skills = [s.strip() for s in pref_skills.split(",") if s.strip()]

    keywords = data.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]

    certifications = data.get("certifications", [])
    if isinstance(certifications, str):
        certifications = [c.strip() for c in certifications.split(",") if c.strip()]

    def safe_float(val, default):
        try:
            return float(val) if val is not None and str(val).strip() != "" else default
        except (ValueError, TypeError):
            return default

    c = Criteria(
        user_id=user_id,
        title=title,
        job_role=job_role,
        industry=industry,
        location=location,
        min_experience=safe_float(data.get("min_experience"), 2.0),
        min_degree=data.get("min_degree") or "Bachelor's",
        branch=data.get("branch") or "Computer Science",
        skill_weight=safe_float(data.get("skill_weight"), 30.0),
        experience_weight=safe_float(data.get("experience_weight"), 25.0),
        education_weight=safe_float(data.get("education_weight"), 15.0),
        certification_weight=safe_float(data.get("certification_weight"), 15.0),
        keyword_weight=safe_float(data.get("keyword_weight"), 15.0),
        is_template=bool(data.get("is_template", False))
    )
    
    c.set_data("required_skills_json", req_skills)
    c.set_data("preferred_skills_json", pref_skills)
    c.set_data("keywords_json", keywords)
    c.set_data("certifications_json", certifications)
    
    db.session.add(c)
    db.session.commit()

    return jsonify({"success": True, "message": "Criteria saved successfully.", "criteria": c.to_dict()})

@criteria_bp.route("/api/criteria/<int:criteria_id>", methods=["DELETE"])
def delete_criteria(criteria_id):
    c = Criteria.query.get_or_404(criteria_id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"success": True, "message": "Criteria deleted."})
