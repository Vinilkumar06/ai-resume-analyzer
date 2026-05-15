# AI Resume Analyzer (No Auth Version)

A focused, fast resume analyzer — upload your resume, paste a job description, get instant ATS score and improvement suggestions. No login required.

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```
API docs: http://localhost:8000/api/docs

### Frontend
```bash
cd frontend
npm install
npm start
```
App: http://localhost:3000

### Docker (all-in-one)
```bash
docker-compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/resume/upload-resume | Upload PDF or DOCX |
| POST | /api/analysis/analyze-resume | Run full NLP analysis |
| GET  | /api/report/generate-report/{id} | Download PDF report |
| GET  | /api/health | Health check |

## Stack
- **Backend**: FastAPI, Motor, MongoDB, scikit-learn, pdfplumber, ReportLab
- **Frontend**: React 18, Recharts, react-dropzone, Tailwind CSS
