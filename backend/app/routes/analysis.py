from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from loguru import logger

from app.database.connection import get_db
from app.schemas.schemas import JobDescriptionInput
from app.services import nlp_service

router = APIRouter()


@router.post("/analyze-resume")
async def analyze_resume(payload: JobDescriptionInput):
    db = get_db()

    resume = await db.resumes.find_one({"_id": ObjectId(payload.resume_id)})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    raw_text = resume.get("raw_text", "")
    jd_text = payload.job_description

    resume_skills = nlp_service.extract_skills(raw_text)
    jd_skills = nlp_service.extract_skills_from_jd(jd_text)

    matched_skills = sorted(list(set(resume_skills) & set(jd_skills)))
    missing_skills = sorted(list(set(jd_skills) - set(resume_skills)))

    skill_match_pct = (
        round(len(matched_skills) / len(jd_skills) * 100, 1) if jd_skills else 0.0
    )

    extracted_info = {
        "skills": resume_skills,
        "education": nlp_service.extract_education(raw_text),
        "experience": nlp_service.extract_experience(raw_text),
        "certifications": nlp_service.extract_certifications(raw_text),
        "projects": nlp_service.extract_projects(raw_text),
        "contact": nlp_service.extract_contact_info(raw_text),
    }

    tfidf_sim = nlp_service.compute_tfidf_similarity(raw_text, jd_text)
    cosine_sim = nlp_service.compute_keyword_cosine_similarity(resume_skills, jd_skills)

    ats_score = nlp_service.calculate_ats_score(
        raw_text, jd_text, resume_skills, jd_skills, extracted_info
    )
    suggestions = nlp_service.generate_suggestions(
        resume_skills, jd_skills, extracted_info, ats_score
    )
    summary = nlp_service.generate_summary(raw_text, extracted_info, ats_score, skill_match_pct)
    job_title = nlp_service.guess_job_title(jd_text)

    analysis_doc = {
        "resume_id": payload.resume_id,
        "filename": resume.get("filename", ""),
        "ats_score": ats_score,
        "skill_match_percentage": skill_match_pct,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
        "summary": summary,
        "extracted_info": extracted_info,
        "tfidf_similarity": tfidf_sim,
        "cosine_similarity": cosine_sim,
        "job_title_guess": job_title,
        "created_at": datetime.utcnow(),
    }

    result = await db.analyses.insert_one(analysis_doc)
    analysis_id = str(result.inserted_id)
    logger.info(f"Analysis complete: {analysis_id}, ATS={ats_score}")

    return {
        "id": analysis_id,
        **{k: v for k, v in analysis_doc.items() if k != "_id"},
        "created_at": analysis_doc["created_at"].isoformat(),
    }
