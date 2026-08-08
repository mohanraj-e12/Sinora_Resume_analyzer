from flask import Blueprint, jsonify, request
from models.resume import Resume
from models.report import Report
from services.ats_engine import calculate_ats_metrics
from services.gemini_service import generate_ai_analysis
from extensions import db

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/api/analysis/<int:id>", methods=["GET"])
def get_analysis(id):
    report = Report.query.get(id)
    if report:
        resume = report.resume
    else:
        resume = Resume.query.get(id)
        if resume:
            report = Report.query.filter_by(resume_id=resume.id).first()
        else:
            return jsonify({"success": False, "message": "Analysis report not found."}), 404
    
    if not report and resume:
        parsed_data = resume.to_dict()
        parsed_data["raw_text"] = resume.raw_text
        ats_metrics = calculate_ats_metrics(parsed_data)
        ai_data = generate_ai_analysis(parsed_data, ats_metrics)
        
        report = Report(
            resume_id=resume.id,
            user_id=resume.user_id,
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
        db.session.commit()

    return jsonify({
        "success": True,
        "resume": resume.to_dict(),
        "report": report.to_dict()
    })

@analysis_bp.route("/api/analysis/reanalyze/<int:resume_id>", methods=["POST"])
def reanalyze_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    payload = request.get_json() or {}
    
    criteria_data = None
    criteria_id = payload.get("criteria_id")
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
        except Exception:
            pass

    if not criteria_data:
        criteria_data = payload.get("criteria_data") or payload
    
    parsed_data = resume.to_dict()
    parsed_data["raw_text"] = resume.raw_text
    
    ats_metrics = calculate_ats_metrics(parsed_data, criteria_data)
    ai_data = generate_ai_analysis(parsed_data, ats_metrics)
    
    report = Report.query.filter_by(resume_id=resume.id).first()
    if not report:
        report = Report(resume_id=resume.id, user_id=resume.user_id)
        
    report.ats_score = ats_metrics["ats_score"]
    report.selection_percentage = ats_metrics["selection_percentage"]
    report.skill_match = ats_metrics["skill_match"]
    report.keyword_match = ats_metrics["keyword_match"]
    report.education_match = ats_metrics["education_match"]
    report.experience_match = ats_metrics["experience_match"]
    report.completeness_score = ats_metrics["completeness_score"]
    report.formatting_score = ats_metrics["formatting_score"]
    report.grammar_score = ats_metrics["grammar_score"]
    report.readability_score = ats_metrics["readability_score"]
    report.overall_quality = ats_metrics["overall_quality"]
    report.professional_summary = ai_data.get("professional_summary")
    report.resume_review = ai_data.get("resume_review")
    report.hr_review = ai_data.get("hr_review")

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

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Re-analysis complete.",
        "report": report.to_dict()
    })
