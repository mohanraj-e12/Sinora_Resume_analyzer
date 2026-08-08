import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from config import Config

def generate_pdf_report(report, resume) -> str:
    reports_dir = Config.REPORTS_FOLDER
    os.makedirs(reports_dir, exist_ok=True)
    
    pdf_filename = f"Sinora_AI_Report_{report.id}_{resume.candidate_name.replace(' ', '_')}.pdf"
    pdf_path = os.path.join(reports_dir, pdf_filename)
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#0d0096'),
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.HexColor('#464554'),
        spaceAfter=20
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#131313'),
        spaceBefore=15,
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#201f1f'),
        spaceAfter=8,
        leading=14
    )

    story = []
    
    # Title Banner
    story.append(Paragraph("SINORA AI - Resume Analysis Report", title_style))
    story.append(Paragraph(f"Candidate: <b>{resume.candidate_name}</b> | Email: {resume.candidate_email} | Generated: {report.created_at.strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    story.append(Spacer(1, 10))

    # Metrics Table
    data = [
        ["Metric", "Score", "Rating"],
        ["Overall ATS Score", f"{report.ats_score}%", report.overall_quality],
        ["Selection Percentage", f"{report.selection_percentage}%", "High Confidence"],
        ["Skill Match", f"{report.skill_match}%", "Validated"],
        ["Keyword Match", f"{report.keyword_match}%", "Optimal"],
        ["Formatting Score", f"{report.formatting_score}%", "Clean ATS Layout"],
        ["Readability Score", f"{report.readability_score}%", "High Clarity"]
    ]

    t = Table(data, colWidths=[200, 150, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8083ff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e2e1')),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # Professional Summary
    story.append(Paragraph("Professional Summary", section_heading))
    story.append(Paragraph(report.professional_summary or "Candidate presents strong technical experience aligned with target role requirements.", body_style))
    story.append(Spacer(1, 10))

    # Key Strengths
    story.append(Paragraph("Key Strengths", section_heading))
    strengths = report.get_data("strengths_json")
    for s in strengths:
        story.append(Paragraph(f"• {s}", body_style))
    story.append(Spacer(1, 10))

    # Potential Gaps
    story.append(Paragraph("Potential Gaps & Recommendations", section_heading))
    weaknesses = report.get_data("weaknesses_json")
    for w in weaknesses:
        story.append(Paragraph(f"• {w}", body_style))
    
    recommendations = report.get_data("recommendations_json")
    for r in recommendations:
        story.append(Paragraph(f"• Recommendation: {r}", body_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph("© 2026 Sinora AI. Precision Engineering for Careers.", subtitle_style))

    doc.build(story)
    return pdf_path
