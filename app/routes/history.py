from flask import Blueprint, request, jsonify
from extensions import db
from models.resume import Resume
from models.report import Report
from models.log import AnalysisLog

history_bp = Blueprint("history", __name__)

@history_bp.route("/api/history", methods=["GET"])
def get_history():
    query = request.args.get("query", "").strip().lower()
    min_score = request.args.get("min_score", type=float)
    max_score = request.args.get("max_score", type=float)
    
    resumes_query = Resume.query

    if query:
        resumes_query = resumes_query.filter(
            (Resume.candidate_name.ilike(f"%{query}%")) |
            (Resume.original_filename.ilike(f"%{query}%")) |
            (Resume.raw_text.ilike(f"%{query}%"))
        )

    resumes = resumes_query.order_by(Resume.upload_date.desc()).all()
    results = []

    for r in resumes:
        report = r.report
        if min_score is not None and report and report.ats_score < min_score:
            continue
        if max_score is not None and report and report.ats_score > max_score:
            continue

        results.append({
            "resume": r.to_dict(),
            "report": report.to_dict() if report else None
        })

    return jsonify({"success": True, "history": results, "count": len(results)})

@history_bp.route("/api/history/<int:resume_id>", methods=["DELETE"])
def delete_history_item(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    db.session.delete(resume)
    db.session.commit()
    return jsonify({"success": True, "message": "Resume and analysis report deleted."})
