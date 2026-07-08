"""
Basic sanity tests for core modules. Run with: pytest tests/
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.skill_extractor import extract_skills, extract_contact_info, detect_sections
from src.ats_scorer import compute_ats_score
from src.job_matcher import match_job_role, list_job_roles

SAMPLE_RESUME = """
John Doe
john.doe@example.com | +1-555-123-4567 | linkedin.com/in/johndoe | github.com/johndoe

SUMMARY
Backend developer with 3 years of experience building scalable APIs.

EXPERIENCE
Built and deployed REST APIs using Python and Flask, serving 10k+ daily users.
Led a team of 3 engineers to migrate services to Docker and AWS.
Improved database query performance by 40% using PostgreSQL indexing.

EDUCATION
B.S. Computer Science, State University

SKILLS
Python, Flask, FastAPI, SQL, PostgreSQL, Docker, AWS, Git, REST API
"""


def test_extract_skills_finds_known_skills():
    skills = extract_skills(SAMPLE_RESUME)
    assert "python" in skills
    assert "flask" in skills
    assert "docker" in skills


def test_extract_contact_info():
    contact = extract_contact_info(SAMPLE_RESUME)
    assert contact["email"] == "john.doe@example.com"
    assert contact["linkedin"] is not None
    assert contact["github"] is not None


def test_detect_sections():
    sections = detect_sections(SAMPLE_RESUME)
    assert "experience" in sections
    assert "education" in sections
    assert "skills" in sections


def test_ats_score_is_within_bounds():
    result = compute_ats_score(SAMPLE_RESUME)
    assert 0 <= result["total_score"] <= 100


def test_job_matcher_backend_role():
    skills = extract_skills(SAMPLE_RESUME)
    assert "Backend Developer" in list_job_roles()
    result = match_job_role(skills, SAMPLE_RESUME, "Backend Developer")
    assert 0 <= result["match_score"] <= 100
    assert "python" in result["matched_required"]
