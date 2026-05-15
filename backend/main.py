from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from loguru import logger

from app.database.connection import connect_db, disconnect_db
from app.routes import resume, analysis, report
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Resume Analyzer API...")
    await connect_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    await disconnect_db()


app = FastAPI(
    title="AI Resume Analyzer API",
    description="Resume analysis with NLP, ATS scoring, and skill matching — no login required",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router,   prefix="/api/resume",   tags=["Resume"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(report.router,   prefix="/api/report",   tags=["Report"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0", "auth": "disabled"}
