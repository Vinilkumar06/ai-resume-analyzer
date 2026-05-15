from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
from bson import ObjectId
from loguru import logger
import uuid

from app.database.connection import get_db
from app.services.file_parser import extract_text
from app.core.config import settings

router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES and not (
        file.filename.endswith(".pdf") or file.filename.endswith(".docx")
    ):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are accepted")

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit")

    raw_text = await extract_text(content, file.content_type or "", file.filename)

    db = get_db()
    session_id = str(uuid.uuid4())
    resume_doc = {
        "session_id": session_id,
        "filename": file.filename,
        "file_type": "pdf" if file.filename.lower().endswith(".pdf") else "docx",
        "raw_text": raw_text,
        "file_size": len(content),
        "uploaded_at": datetime.utcnow(),
    }
    result = await db.resumes.insert_one(resume_doc)
    resume_id = str(result.inserted_id)
    logger.info(f"Resume uploaded: {resume_id} ({file.filename})")

    return {
        "resume_id": resume_id,
        "filename": file.filename,
        "message": "Resume uploaded and parsed successfully",
        "text_length": len(raw_text),
    }
