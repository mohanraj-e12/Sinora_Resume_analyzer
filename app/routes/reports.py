import os
from flask import Blueprint, send_file, jsonify, current_app
from models.report import Report
from models.resume import Resume
from services.pdf_service import generate_pdf_report

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/api/reports/download/<int:report_id>", methods=["GET"])
def download_pdf_report(report_id):
    report = Report.query.get_or_404(report_id)
    resume = Resume.query.get(report.resume_id)
    
    if not report.pdf_report_path or not os.path.exists(report.pdf_report_path):
        pdf_path = generate_pdf_report(report, resume)
        report.pdf_report_path = pdf_path
        from extensions import db
        db.session.commit()
    else:
        pdf_path = report.pdf_report_path

    return send_file(pdf_path, as_attachment=True, download_name=os.path.basename(pdf_path))
