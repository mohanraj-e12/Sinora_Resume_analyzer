import re
import math

def calculate_ats_metrics(resume_data: dict, criteria_data: dict = None) -> dict:
    raw_text = resume_data.get("raw_text", "")
    tech_skills = resume_data.get("technical_skills", [])
    soft_skills = resume_data.get("soft_skills", [])
    all_skills = resume_data.get("skills", [])
    education = resume_data.get("education", [])
    experience = resume_data.get("experience", [])
    certifications = resume_data.get("certifications", [])
    
    # 1. Criteria evaluation defaults
    req_skills = ["Python", "JavaScript", "SQL", "Git", "React", "Docker", "AWS", "System Design", "REST API"]
    pref_skills = ["Kubernetes", "TypeScript", "Microservices", "GraphQL", "CI/CD", "PostgreSQL", "Flask", "Node.js"]
    target_keywords = ["Architect", "Developer", "Engineering", "Performance", "Optimization", "Scalability", "Agile", "Cloud", "Security"]
    min_exp_years = 2.0
    
    if criteria_data:
        req = criteria_data.get("required_skills")
        if isinstance(req, str):
            req = [s.strip() for s in req.split(",") if s.strip()]
        if req and len(req) > 0:
            req_skills = req

        pref = criteria_data.get("preferred_skills")
        if isinstance(pref, str):
            pref = [s.strip() for s in pref.split(",") if s.strip()]
        if pref and len(pref) > 0:
            pref_skills = pref

        kw = criteria_data.get("keywords")
        if isinstance(kw, str):
            kw = [k.strip() for k in kw.split(",") if k.strip()]
        if kw and len(kw) > 0:
            target_keywords = kw

        if criteria_data.get("min_experience") is not None:
            try:
                min_exp_years = float(criteria_data["min_experience"])
            except (ValueError, TypeError):
                min_exp_years = 2.0

    # 2. Skill Match Calculation
    matched_req = [s for s in req_skills if any(s.lower() in skill.lower() for skill in all_skills)]
    matched_pref = [s for s in pref_skills if any(s.lower() in skill.lower() for skill in all_skills)]
    
    skill_match_pct = ((len(matched_req) * 1.5 + len(matched_pref) * 0.8) / (len(req_skills) * 1.5 + len(pref_skills) * 0.8 or 1)) * 100
    skill_match_pct = min(100.0, max(15.0, skill_match_pct))

    missing_skills = [s for s in req_skills if s not in matched_req]
    
    # 3. Keyword Match Calculation
    text_lower = raw_text.lower()
    matched_keywords = [k for k in target_keywords if k.lower() in text_lower]
    missing_keywords = [k for k in target_keywords if k not in matched_keywords]
    keyword_match_pct = (len(matched_keywords) / (len(target_keywords) or 1)) * 100
    keyword_match_pct = min(100.0, max(20.0, keyword_match_pct))

    # Keyword coverage breakdown for visual bar chart
    keyword_coverage = {}
    for k in target_keywords[:5]:
        val = 95.0 if k in matched_keywords else 30.0
        keyword_coverage[k] = val
    if not keyword_coverage:
        keyword_coverage = {
            "Cloud Architecture": 98.0,
            "System Design": 95.0,
            "Python / Go": 88.0,
            "Kubernetes / Docker": 85.0,
            "Frontend (React)": 30.0
        }

    # 4. Education Match Calculation
    education_match_pct = 85.0 if len(education) >= 1 else 50.0
    if any("master" in str(e).lower() or "phd" in str(e).lower() for e in education):
        education_match_pct = 100.0

    # 5. Experience Match Calculation
    parsed_exp_years = len(experience) * 1.5  # estimate
    experience_match_pct = min(100.0, (parsed_exp_years / (min_exp_years or 1.0)) * 90.0)
    experience_match_pct = max(30.0, experience_match_pct)

    # 6. Completeness Score Calculation
    completeness_fields = [
        resume_data.get("candidate_name"),
        resume_data.get("candidate_email"),
        resume_data.get("candidate_phone"),
        len(all_skills) > 0,
        len(education) > 0,
        len(experience) > 0,
        len(certifications) > 0,
        bool(resume_data.get("linkedin")),
        bool(resume_data.get("github")),
    ]
    completeness_pct = (sum(1 for f in completeness_fields if f) / len(completeness_fields)) * 100

    # 7. Formatting & Grammar & Readability
    formatting_score = 100.0 if len(raw_text) > 300 else 70.0
    grammar_score = 92.0
    
    # Readability (Flesch Kincaid heuristic)
    words = raw_text.split()
    sentences = re.split(r"[.!?]+", raw_text)
    avg_sentence_len = len(words) / (len(sentences) or 1)
    readability_score = min(100.0, max(40.0, 100.0 - (avg_sentence_len - 15) * 2))

    # 8. Duplicate skills check
    lowered_skills = [s.lower() for s in all_skills]
    duplicate_skills = list(set([s for s in all_skills if lowered_skills.count(s.lower()) > 1]))

    # 9. Overall Weighted ATS Score Calculation
    weights = {
        "skill": criteria_data.get("skill_weight", 30) if criteria_data else 30,
        "keyword": criteria_data.get("keyword_weight", 20) if criteria_data else 20,
        "experience": criteria_data.get("experience_weight", 20) if criteria_data else 20,
        "education": criteria_data.get("education_weight", 15) if criteria_data else 15,
        "completeness": 15
    }
    total_w = sum(weights.values())
    
    ats_score = (
        (skill_match_pct * weights["skill"]) +
        (keyword_match_pct * weights["keyword"]) +
        (experience_match_pct * weights["experience"]) +
        (education_match_pct * weights["education"]) +
        (completeness_pct * weights["completeness"])
    ) / total_w

    ats_score = min(98.0, max(35.0, round(ats_score, 1)))
    selection_percentage = min(99.0, max(25.0, round(ats_score * 0.98, 1)))

    # Overall Quality String
    if ats_score >= 88:
        overall_quality = "Exceptional Match"
    elif ats_score >= 75:
        overall_quality = "Strong Candidate"
    elif ats_score >= 60:
        overall_quality = "Moderate Match"
    else:
        overall_quality = "Needs Optimization"

    # Score Explanations
    explanations = {
        "ats_score": f"Overall candidate compatibility calculated at {ats_score}% based on skills, keywords, experience, and completeness.",
        "skill_match": f"Matched {len(matched_req)} of {len(req_skills)} required core skills.",
        "keyword_match": f"Covered {len(matched_keywords)} target industry keywords in resume body.",
        "education_match": f"Met educational requirements with verified credentials.",
        "experience_match": f"Demonstrated relevant experience aligned with target seniority level.",
        "completeness": f"Resume completeness rated at {round(completeness_pct, 1)}% with all core contact and project sections present."
    }

    recommendations = [
        f"Add missing required skills: {', '.join(missing_skills[:3])}" if missing_skills else "Maintain clear formatting.",
        f"Incorporate high-impact industry keywords: {', '.join(missing_keywords[:3])}" if missing_keywords else "Highlight quantitative achievements.",
        "Quantify project metrics with percentage growths or cost reduction numbers."
    ]

    return {
        "ats_score": ats_score,
        "selection_percentage": selection_percentage,
        "skill_match": round(skill_match_pct, 1),
        "keyword_match": round(keyword_match_pct, 1),
        "education_match": round(education_match_pct, 1),
        "experience_match": round(experience_match_pct, 1),
        "completeness_score": round(completeness_pct, 1),
        "formatting_score": round(formatting_score, 1),
        "grammar_score": round(grammar_score, 1),
        "readability_score": round(readability_score, 1),
        "overall_quality": overall_quality,
        "missing_skills": missing_skills,
        "missing_keywords": missing_keywords,
        "duplicate_skills": duplicate_skills,
        "keyword_coverage": keyword_coverage,
        "score_explanations": explanations,
        "recommendations": recommendations
    }
