"""
Matches a resume against a target job role.
Combines:
  1. Direct skill-list overlap (required vs preferred skills)
  2. TF-IDF cosine similarity between resume text and job role skill text
     (demonstrates a lightweight ML/NLP similarity technique)
"""
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import JOB_ROLES_PATH

with open(JOB_ROLES_PATH, "r", encoding="utf-8") as f:
    JOB_ROLES = json.load(f)


def list_job_roles() -> list[str]:
    return list(JOB_ROLES.keys())


def match_job_role(resume_skills: list[str], resume_text: str, job_role: str) -> dict:
    role = JOB_ROLES.get(job_role)
    if not role:
        raise ValueError(f"Unknown job role: {job_role}")

    required = set(s.lower() for s in role["required"])
    preferred = set(s.lower() for s in role["preferred"])
    resume_skill_set = set(s.lower() for s in resume_skills)

    matched_required = sorted(required & resume_skill_set)
    missing_required = sorted(required - resume_skill_set)
    matched_preferred = sorted(preferred & resume_skill_set)
    missing_preferred = sorted(preferred - resume_skill_set)

    required_score = (len(matched_required) / len(required) * 100) if required else 100
    preferred_score = (len(matched_preferred) / len(preferred) * 100) if preferred else 100

    # Weighted skill overlap score: required skills matter more than preferred
    overlap_score = round(required_score * 0.7 + preferred_score * 0.3, 1)

    # TF-IDF similarity between full resume text and the role's skill keywords
    job_text = " ".join(sorted(required | preferred))
    similarity_score = _tfidf_similarity(resume_text, job_text)

    # Final match score blends explicit overlap with semantic similarity
    final_score = round(overlap_score * 0.75 + similarity_score * 0.25, 1)

    return {
        "job_role": job_role,
        "match_score": final_score,
        "overlap_score": overlap_score,
        "similarity_score": similarity_score,
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
    }


def _tfidf_similarity(text_a: str, text_b: str) -> float:
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf = vectorizer.fit_transform([text_a, text_b])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(float(score) * 100, 1)
    except Exception:
        return 0.0
