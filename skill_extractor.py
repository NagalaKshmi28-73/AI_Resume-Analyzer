"""
Extracts skills, contact info, and structural sections from resume text
using keyword matching against a curated skills database.
"""
import json
import re
from config import SKILLS_DB_PATH

with open(SKILLS_DB_PATH, "r", encoding="utf-8") as f:
    SKILLS_DB = json.load(f)

ALL_SKILLS = sorted(
    {skill.lower() for category in SKILLS_DB.values() for skill in category},
    key=len,
    reverse=True,  # match longer phrases first, e.g. "machine learning" before "learning"
)

SECTION_HEADERS = [
    "experience", "work experience", "education", "skills", "projects",
    "certifications", "summary", "objective", "achievements", "publications",
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s-]?)?(\(?\d{3,4}\)?[\s-]?)\d{3,4}[\s-]?\d{3,4}")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[A-Za-z0-9\-_/]+", re.IGNORECASE)
GITHUB_RE = re.compile(r"github\.com/[A-Za-z0-9\-_/]+", re.IGNORECASE)


def extract_skills(resume_text: str) -> list[str]:
    """Return the list of known skills found in the resume text."""
    text_lower = resume_text.lower()
    found = []
    for skill in ALL_SKILLS:
        # word-boundary-ish match so "r" or "go" don't match inside other words
        pattern = r"(?<![a-zA-Z0-9+#.])" + re.escape(skill) + r"(?![a-zA-Z0-9+#])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def extract_contact_info(resume_text: str) -> dict:
    email = EMAIL_RE.search(resume_text)
    phone = PHONE_RE.search(resume_text)
    linkedin = LINKEDIN_RE.search(resume_text)
    github = GITHUB_RE.search(resume_text)
    return {
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
    }


def detect_sections(resume_text: str) -> list[str]:
    text_lower = resume_text.lower()
    return [header for header in SECTION_HEADERS if header in text_lower]


def word_count(resume_text: str) -> int:
    return len(resume_text.split())


def count_action_verbs(resume_text: str) -> int:
    action_verbs = [
        "led", "built", "developed", "designed", "implemented", "created",
        "managed", "improved", "increased", "reduced", "launched", "optimized",
        "automated", "architected", "delivered", "achieved", "spearheaded",
        "collaborated", "analyzed", "engineered",
    ]
    text_lower = resume_text.lower()
    return sum(len(re.findall(r"\b" + verb + r"\b", text_lower)) for verb in action_verbs)
