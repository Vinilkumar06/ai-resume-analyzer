from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from bson import ObjectId

from app.database.connection import get_db
from app.services.report_service import generate_analysis_pdf

router = APIRouter()


@router.get("/generate-report/{analysis_id}")
async def generate_report(analysis_id: str):
    db = get_db()
    analysis = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis_data = dict(analysis)
    analysis_data["id"] = str(analysis_data.pop("_id"))

    pdf_bytes = generate_analysis_pdf(analysis_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="resume_analysis_{analysis_id[:8]}.pdf"'
        },
    )
