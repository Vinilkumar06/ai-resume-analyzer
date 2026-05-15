from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class JobDescriptionInput(BaseModel):
    job_description: str = Field(..., min_length=50)
    resume_id: str


class AnalysisOut(BaseModel):
    id: str
    resume_id: str
    ats_score: float
    skill_match_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: List[str]
    summary: str
    extracted_info: Dict[str, Any]
    tfidf_similarity: float
    cosine_similarity: float
    job_title_guess: Optional[str]
    created_at: datetime
