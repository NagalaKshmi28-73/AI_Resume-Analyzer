"""
Computes an overall ATS (Applicant Tracking System) compatibility score
based on structural and content heuristics, independent of any specific
job role. This estimates how well an ATS would parse and rank the resume.
"""
from src.skill_extractor import (
    extract_contact_info,
    detect_sections,
    word_count,
    count_action_verbs,
)

IDEAL_MIN_WORDS = 300
IDEAL_MAX_WORDS = 900
IMPORTANT_SECTIONS = ["experience", "education", "skills"]


def compute_ats_score(resume_text: str) -> dict:
    contact = extract_contact_info(resume_text)
    sections = detect_sections(resume_text)
    words = word_count(resume_text)
    verbs = count_action_verbs(resume_text)

    breakdown = {}

    # 1. Contact info completeness (20 pts)
    contact_points = 0
    if contact["email"]:
        contact_points += 8
    if contact["phone"]:
        contact_points += 6
    if contact["linkedin"] or contact["github"]:
        contact_points += 6
    breakdown["contact_info"] = {"score": contact_points, "max": 20}

    # 2. Section coverage (30 pts)
    found_important = [s for s in IMPORTANT_SECTIONS if s in sections]
    section_points = round((len(found_important) / len(IMPORTANT_SECTIONS)) * 25, 1)
    bonus_sections = min(len(sections) - len(found_important), 3)  # up to 5 bonus pts
    section_points = min(30, section_points + bonus_sections * (5 / 3))
    breakdown["section_coverage"] = {"score": round(section_points, 1), "max": 30}

    # 3. Length appropriateness (20 pts)
    if IDEAL_MIN_WORDS <= words <= IDEAL_MAX_WORDS:
        length_points = 20
    elif words < IDEAL_MIN_WORDS:
        length_points = round(max(0, (words / IDEAL_MIN_WORDS) * 20), 1)
    else:
        overflow_ratio = min(1, (words - IDEAL_MAX_WORDS) / IDEAL_MAX_WORDS)
        length_points = round(max(8, 20 - overflow_ratio * 12), 1)
    breakdown["length"] = {"score": length_points, "max": 20, "word_count": words}

    # 4. Action-verb usage / impact language (20 pts)
    verb_points = min(20, verbs * 1.5)
    breakdown["action_verbs"] = {"score": round(verb_points, 1), "max": 20, "count": verbs}

    # 5. Formatting sanity check (10 pts)
    # Very short extracted text relative to typical resumes suggests a
    # graphics-heavy / image-based / table-heavy PDF an ATS can't parse well.
    formatting_points = 10 if words > 100 else 3
    breakdown["formatting"] = {"score": formatting_points, "max": 10}

    total = sum(item["score"] for item in breakdown.values())
    total = round(min(100, total), 1)

    return {
        "total_score": total,
        "breakdown": breakdown,
        "contact_info": contact,
        "sections_found": sections,
    }
