import re
import string
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

# ---------------------------------------------------------------------------
# Comprehensive skills knowledge base
# ---------------------------------------------------------------------------
SKILLS_DB = {
    "programming": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
        "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
        "bash", "shell", "powershell", "dart", "elixir", "haskell", "lua",
    ],
    "web_frontend": [
        "react", "vue", "angular", "svelte", "nextjs", "gatsby", "nuxt",
        "html", "css", "sass", "tailwind", "bootstrap", "material ui",
        "redux", "mobx", "zustand", "webpack", "vite", "jquery",
    ],
    "web_backend": [
        "fastapi", "django", "flask", "express", "nodejs", "spring boot",
        "rails", "laravel", "asp.net", "nestjs", "graphql", "rest api",
        "microservices", "grpc", "websockets",
    ],
    "databases": [
        "mongodb", "postgresql", "mysql", "sqlite", "redis", "elasticsearch",
        "cassandra", "dynamodb", "firebase", "supabase", "neo4j", "oracle",
        "sql server", "mariadb", "influxdb",
    ],
    "cloud": [
        "aws", "azure", "gcp", "google cloud", "heroku", "vercel", "netlify",
        "digitalocean", "cloudflare", "lambda", "ec2", "s3", "rds",
        "kubernetes", "docker", "terraform", "ansible", "pulumi",
    ],
    "ai_ml": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
        "matplotlib", "seaborn", "hugging face", "llm", "openai", "langchain",
        "spark", "hadoop", "data science", "neural networks", "transformers",
    ],
    "devops": [
        "ci/cd", "jenkins", "github actions", "gitlab ci", "circleci",
        "docker", "kubernetes", "helm", "prometheus", "grafana", "elk stack",
        "nginx", "apache", "linux", "git", "agile", "scrum", "devops",
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "critical thinking", "project management", "time management",
        "collaboration", "mentoring", "presentation", "analytical",
    ],
    "certifications": [
        "aws certified", "azure certified", "gcp certified", "pmp", "cissp",
        "cka", "ckad", "comptia", "cisco", "oracle certified", "google certified",
    ],
}

ALL_SKILLS = {skill for skills in SKILLS_DB.values() for skill in skills}


def preprocess_text(text: str) -> str:
    """Clean and normalize text for NLP processing."""
    text = text.lower()
    text = re.sub(r'[^\w\s\+\#\/]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_skills(text: str) -> List[str]:
    """Extract skills from resume text using keyword matching."""
    processed = preprocess_text(text)
    found_skills = []
    for skill in ALL_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, processed):
            found_skills.append(skill)
    return sorted(list(set(found_skills)))


def extract_skills_from_jd(text: str) -> List[str]:
    """Extract required skills from job description."""
    return extract_skills(text)


def extract_education(text: str) -> List[str]:
    """Extract education information."""
    education = []
    patterns = [
        r'\b(bachelor|b\.?s\.?|b\.?e\.?|b\.?tech|b\.?sc)\b[^\n]*',
        r'\b(master|m\.?s\.?|m\.?e\.?|m\.?tech|mba|m\.?sc)\b[^\n]*',
        r'\b(ph\.?d|doctorate|doctor)\b[^\n]*',
        r'\b(associate|diploma|certificate)\b[^\n]*',
        r'\b(computer science|information technology|engineering|mathematics|physics|statistics)\b[^\n]*',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            cleaned = m.strip()[:120]
            if cleaned and cleaned not in education:
                education.append(cleaned)
    return education[:6]


def extract_experience(text: str) -> List[str]:
    """Extract work experience mentions."""
    experience = []
    patterns = [
        r'(\d+[\+]?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp))',
        r'((?:senior|junior|lead|principal|staff)\s+\w+\s+(?:engineer|developer|analyst|manager|architect))',
        r'(\w+\s+(?:engineer|developer|analyst|manager|designer|architect|consultant))\s+(?:at|@)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            item = m.strip() if isinstance(m, str) else m[0].strip()
            if item and item not in experience:
                experience.append(item[:100])
    return experience[:8]


def extract_certifications(text: str) -> List[str]:
    """Extract certifications."""
    certs = []
    patterns = [
        r'\b(aws\s+certified\s+\w+(?:\s+\w+)?)',
        r'\b(microsoft\s+certified\s+\w+(?:\s+\w+)?)',
        r'\b(google\s+(?:cloud\s+)?certified\s+\w+(?:\s+\w+)?)',
        r'\b(pmp|cissp|ceh|comptia\s+\w+|ccna|ccnp|cka|ckad)\b',
        r'(certified\s+\w+(?:\s+\w+){0,3})',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            item = m.strip()
            if item and item not in certs:
                certs.append(item[:100])
    return certs[:6]


def extract_projects(text: str) -> List[str]:
    """Extract project names/descriptions."""
    projects = []
    # Look for project section
    project_section = re.search(
        r'(?:projects?|portfolio)[:\s]+(.*?)(?=\n(?:education|experience|skills|certification)|$)',
        text, re.IGNORECASE | re.DOTALL
    )
    if project_section:
        block = project_section.group(1)
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        for line in lines[:6]:
            if len(line) > 10:
                projects.append(line[:120])
    return projects


def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract contact information."""
    contact = {}
    email_match = re.search(r'\b[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}\b', text)
    if email_match:
        contact["email"] = email_match.group()
    phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,15}', text)
    if phone_match:
        contact["phone"] = phone_match.group().strip()
    linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
    if linkedin_match:
        contact["linkedin"] = linkedin_match.group()
    github_match = re.search(r'github\.com/[\w\-]+', text, re.IGNORECASE)
    if github_match:
        contact["github"] = github_match.group()
    return contact


def compute_tfidf_similarity(resume_text: str, job_text: str) -> float:
    """Compute TF-IDF based cosine similarity between resume and JD."""
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000,
        )
        texts = [preprocess_text(resume_text), preprocess_text(job_text)]
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(similarity) * 100, 2)
    except Exception as e:
        logger.error(f"TF-IDF similarity error: {e}")
        return 0.0


def compute_keyword_cosine_similarity(resume_skills: List[str], jd_skills: List[str]) -> float:
    """Cosine similarity based on skill vectors."""
    if not jd_skills:
        return 0.0
    all_skills = list(set(resume_skills + jd_skills))
    resume_vec = [1 if s in resume_skills else 0 for s in all_skills]
    jd_vec = [1 if s in jd_skills else 0 for s in all_skills]
    dot = sum(a * b for a, b in zip(resume_vec, jd_vec))
    mag_r = sum(a ** 2 for a in resume_vec) ** 0.5
    mag_j = sum(b ** 2 for b in jd_vec) ** 0.5
    if mag_r == 0 or mag_j == 0:
        return 0.0
    return round((dot / (mag_r * mag_j)) * 100, 2)


def calculate_ats_score(
    resume_text: str,
    job_text: str,
    resume_skills: List[str],
    jd_skills: List[str],
    extracted_info: Dict,
) -> float:
    """Calculate comprehensive ATS score (0–100)."""
    score = 0.0

    # Skill match component (40%)
    if jd_skills:
        matched = len(set(resume_skills) & set(jd_skills))
        skill_ratio = matched / len(jd_skills)
        score += skill_ratio * 40

    # TF-IDF similarity (25%)
    tfidf = compute_tfidf_similarity(resume_text, job_text)
    score += (tfidf / 100) * 25

    # Structure completeness (20%)
    structure_score = 0
    if extracted_info.get("education"):
        structure_score += 5
    if extracted_info.get("experience"):
        structure_score += 5
    if extracted_info.get("skills"):
        structure_score += 5
    if extracted_info.get("contact", {}).get("email"):
        structure_score += 3
    if extracted_info.get("certifications"):
        structure_score += 2
    score += structure_score

    # Keyword density (15%)
    jd_keywords = set(preprocess_text(job_text).split())
    resume_words = set(preprocess_text(resume_text).split())
    keyword_overlap = len(jd_keywords & resume_words) / max(len(jd_keywords), 1)
    score += keyword_overlap * 15

    return round(min(score, 100), 1)


def generate_suggestions(
    resume_skills: List[str],
    jd_skills: List[str],
    extracted_info: Dict,
    ats_score: float,
) -> List[str]:
    """Generate actionable resume improvement suggestions."""
    suggestions = []
    missing = set(jd_skills) - set(resume_skills)

    if missing:
        top_missing = list(missing)[:5]
        suggestions.append(
            f"Add these high-priority skills to your resume: {', '.join(top_missing)}"
        )

    if not extracted_info.get("contact", {}).get("email"):
        suggestions.append("Add a professional email address to your contact section.")

    if not extracted_info.get("certifications"):
        suggestions.append(
            "Consider obtaining relevant certifications (e.g., AWS, Google Cloud, PMP) to boost credibility."
        )

    if not extracted_info.get("projects"):
        suggestions.append(
            "Add a Projects section showcasing 2–3 key projects with technologies used and measurable results."
        )

    if ats_score < 50:
        suggestions.append(
            "Your resume has low keyword alignment. Mirror the exact language used in the job description."
        )
        suggestions.append(
            "Use a clean, single-column resume format to improve ATS parsing accuracy."
        )

    if ats_score < 70:
        suggestions.append(
            "Quantify your achievements with metrics (e.g., 'Reduced load time by 40%', 'Led a team of 8')."
        )

    if len(resume_skills) < 10:
        suggestions.append(
            "Expand your Skills section — list both technical and soft skills relevant to the role."
        )

    suggestions.append(
        "Use strong action verbs: Built, Designed, Optimized, Led, Implemented, Architected."
    )
    suggestions.append(
        "Keep your resume to 1–2 pages and ensure consistent formatting throughout."
    )

    return suggestions[:8]


def generate_summary(
    resume_text: str,
    extracted_info: Dict,
    ats_score: float,
    skill_match: float,
) -> str:
    """Generate a concise resume analysis summary."""
    skills_count = len(extracted_info.get("skills", []))
    edu = extracted_info.get("education", [])
    edu_str = edu[0] if edu else "not specified"

    level = "excellent" if ats_score >= 80 else "good" if ats_score >= 60 else "moderate" if ats_score >= 40 else "low"

    return (
        f"This resume demonstrates {level} alignment with the target role, achieving an ATS score of {ats_score:.1f}/100 "
        f"and a skill match of {skill_match:.1f}%. The candidate highlights {skills_count} technical/professional skills. "
        f"Education background: {edu_str}. "
        f"{'Strong keyword alignment detected.' if ats_score >= 70 else 'Keyword optimization is recommended to improve ATS performance.'} "
        f"{'The profile is competitive for this position.' if skill_match >= 60 else 'Targeted skill development could significantly strengthen this application.'}"
    )


def guess_job_title(jd_text: str) -> str:
    """Guess the job title from the JD."""
    titles = [
        "Software Engineer", "Data Scientist", "Machine Learning Engineer",
        "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "DevOps Engineer", "Cloud Architect", "Product Manager",
        "Data Analyst", "Mobile Developer", "Security Engineer",
        "AI Engineer", "NLP Engineer", "Platform Engineer",
    ]
    jd_lower = jd_text.lower()
    for title in titles:
        if title.lower() in jd_lower:
            return title
    return "Software Professional"
