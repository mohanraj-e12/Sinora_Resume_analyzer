import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from models.resume import Resume
from models.report import Report
from models.log import AnalysisLog
from services.parser import extract_text_from_file, process_zip_file, parse_resume_text
from services.ats_engine import calculate_ats_metrics
from services.gemini_service import generate_ai_analysis
from utils.validators import allowed_file, sanitize_filename, MAX_FILE_SIZE

upload_bp = Blueprint("upload", __name__)

from routes.settings import get_current_active_user

def get_current_user_id():
    if current_user and current_user.is_authenticated:
        return current_user.id
    active_user = get_current_active_user()
    return active_user.id if active_user else 1

@upload_bp.route("/api/upload", methods=["POST"])
def upload_resumes():
    if "files" not in request.files and "file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded."}), 400

    uploaded_files = request.files.getlist("files") or [request.files.get("file")]
    criteria_id = request.form.get("criteria_id")
    
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    
    user_id = get_current_user_id()
    processed_resumes = []
    errors = []

    for file_obj in uploaded_files:
        if not file_obj or file_obj.filename == "":
            continue

        original_fn = sanitize_filename(file_obj.filename)
        ext = original_fn.rsplit(".", 1)[-1].lower() if "." in original_fn else ""

        if ext not in ["pdf", "doc", "docx", "zip"]:
            errors.append(f"{original_fn}: Invalid file type. Allowed: PDF, DOC, DOCX, ZIP.")
            continue

        unique_fn = f"{uuid.uuid4().hex}_{original_fn}"
        file_path = os.path.join(upload_folder, unique_fn)
        file_obj.save(file_path)
        file_size = os.path.getsize(file_path)

        if file_size > MAX_FILE_SIZE:
            os.remove(file_path)
            errors.append(f"{original_fn}: File exceeds maximum limit of 50MB.")
            continue

        # Handle ZIP file containing resumes
        if ext == "zip":
            extracted_items = process_zip_file(file_path, upload_folder)
            if not extracted_items:
                errors.append(f"{original_fn}: No valid PDF, DOC, or DOCX resume files found inside ZIP archive.")
            else:
                for item_fn, item_path, item_ext in extracted_items:
                    res_obj, err = process_single_file(item_path, item_fn, item_ext, user_id, criteria_id)
                    if res_obj:
                        processed_resumes.append(res_obj)
                    elif err:
                        errors.append(err)
            
            # Remove temporary container ZIP archive
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
        else:
            res_obj, err = process_single_file(file_path, original_fn, ext, user_id, criteria_id)
            if res_obj:
                processed_resumes.append(res_obj)
            elif err:
                errors.append(err)

    if not processed_resumes and errors:
        return jsonify({"success": False, "message": "Failed to process uploaded files.", "errors": errors}), 400

    return jsonify({
        "success": True,
        "message": f"Successfully processed {len(processed_resumes)} resume(s).",
        "resumes": [r.to_dict() for r in processed_resumes],
        "reports": [r.report.to_dict() for r in processed_resumes if r.report],
        "errors": errors
    })

def process_single_file(file_path, original_filename, ext, user_id, criteria_id=None):
    try:
        # Load criteria if criteria_id provided
        criteria_data = None
        if criteria_id:
            try:
                from models.criteria import Criteria
                crit_id_int = int(criteria_id) if str(criteria_id).isdigit() else None
                if crit_id_int:
                    crit = Criteria.query.get(crit_id_int)
                    if crit:
                        criteria_data = {
                            "id": crit.id,
                            "title": crit.title,
                            "job_role": crit.job_role,
                            "required_skills": crit.get_data("required_skills_json") or [],
                            "preferred_skills": crit.get_data("preferred_skills_json") or [],
                            "keywords": crit.get_data("keywords_json") or [],
                            "certifications": crit.get_data("certifications_json") or [],
                            "min_experience": float(crit.min_experience or 2.0),
                            "min_degree": crit.min_degree or "Bachelor's",
                            "skill_weight": float(crit.skill_weight if crit.skill_weight is not None else 30.0),
                            "experience_weight": float(crit.experience_weight if crit.experience_weight is not None else 25.0),
                            "education_weight": float(crit.education_weight if crit.education_weight is not None else 15.0),
                            "certification_weight": float(crit.certification_weight if crit.certification_weight is not None else 15.0),
                            "keyword_weight": float(crit.keyword_weight if crit.keyword_weight is not None else 15.0)
                        }
            except Exception as crit_err:
                current_app.logger.error(f"Error loading criteria {criteria_id}: {crit_err}")

        raw_text = extract_text_from_file(file_path)
        if not raw_text or len(raw_text.strip()) < 20:
            return None, f"{original_filename}: Corrupted or empty file text."

        parsed_data = parse_resume_text(raw_text, original_filename)

        resume = Resume(
            user_id=user_id,
            filename=os.path.basename(file_path),
            original_filename=original_filename,
            file_type=ext.upper(),
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            candidate_name=parsed_data.get("candidate_name"),
            candidate_email=parsed_data.get("candidate_email"),
            candidate_phone=parsed_data.get("candidate_phone"),
            candidate_address=parsed_data.get("candidate_address"),
            linkedin=parsed_data.get("linkedin"),
            github=parsed_data.get("github"),
            portfolio=parsed_data.get("portfolio"),
            raw_text=raw_text
        )
        
        resume.set_data("education_json", parsed_data.get("education"))
        resume.set_data("experience_json", parsed_data.get("experience"))
        resume.set_data("projects_json", parsed_data.get("projects"))
        resume.set_data("skills_json", parsed_data.get("skills"))
        resume.set_data("technical_skills_json", parsed_data.get("technical_skills"))
        resume.set_data("soft_skills_json", parsed_data.get("soft_skills"))
        resume.set_data("certifications_json", parsed_data.get("certifications"))
        resume.set_data("languages_json", parsed_data.get("languages"))
        resume.set_data("achievements_json", parsed_data.get("achievements"))
        
        db.session.add(resume)
        db.session.commit()

        # Calculate ATS Metrics using custom criteria if available
        ats_metrics = calculate_ats_metrics(parsed_data, criteria_data)

        # AI Analysis via Gemini API
        ai_data = generate_ai_analysis(parsed_data, ats_metrics)

        report = Report(
            resume_id=resume.id,
            user_id=user_id,
            ats_score=ats_metrics["ats_score"],
            selection_percentage=ats_metrics["selection_percentage"],
            skill_match=ats_metrics["skill_match"],
            keyword_match=ats_metrics["keyword_match"],
            education_match=ats_metrics["education_match"],
            experience_match=ats_metrics["experience_match"],
            completeness_score=ats_metrics["completeness_score"],
            formatting_score=ats_metrics["formatting_score"],
            grammar_score=ats_metrics["grammar_score"],
            readability_score=ats_metrics["readability_score"],
            overall_quality=ats_metrics["overall_quality"],
            professional_summary=ai_data.get("professional_summary"),
            resume_review=ai_data.get("resume_review"),
            hr_review=ai_data.get("hr_review")
        )

        report.set_data("missing_skills_json", ats_metrics["missing_skills"])
        report.set_data("missing_keywords_json", ats_metrics["missing_keywords"])
        report.set_data("duplicate_skills_json", ats_metrics["duplicate_skills"])
        report.set_data("recommendations_json", ats_metrics["recommendations"])
        report.set_data("keyword_coverage_json", ats_metrics["keyword_coverage"])
        report.set_data("strengths_json", ai_data.get("strengths", []))
        report.set_data("weaknesses_json", ai_data.get("weaknesses", []))
        report.set_data("improvement_suggestions_json", ai_data.get("improvement_suggestions", []))
        report.set_data("interview_readiness_json", ai_data.get("interview_readiness", {}))
        report.set_data("optimization_tips_json", ai_data.get("optimization_tips", []))
        report.set_data("career_suggestions_json", ai_data.get("career_suggestions", []))
        report.set_data("job_recommendations_json", ai_data.get("job_recommendations", []))
        report.set_data("score_explanations_json", ats_metrics["score_explanations"])

        db.session.add(report)

        # Log action
        log = AnalysisLog(
            user_id=user_id,
            resume_id=resume.id,
            action="RESUME_PARSED",
            message=f"Successfully extracted & analyzed {original_filename} (ATS: {ats_metrics['ats_score']}%)",
            log_type="INFO"
        )
        db.session.add(log)
        db.session.commit()

        return resume, None

    except Exception as e:
        db.session.rollback()
        return None, f"Error processing {original_filename}: {str(e)}"
