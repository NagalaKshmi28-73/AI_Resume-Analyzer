"""
Calls an LLM (OpenAI or Gemini, configurable) to generate qualitative
resume feedback that goes beyond keyword matching: rewrite suggestions,
tone/clarity feedback, and a short summary.
"""
import json
import config

PROMPT_TEMPLATE = """You are an expert technical resume reviewer and career coach.

Analyze the resume text below for a candidate targeting the role of "{job_role}".

RESUME TEXT:
---
{resume_text}
---

MISSING REQUIRED SKILLS FOR THIS ROLE: {missing_required}
MISSING PREFERRED SKILLS FOR THIS ROLE: {missing_preferred}

Respond ONLY with valid JSON (no markdown fences, no preamble) matching this schema:
{{
  "summary": "2-3 sentence overall assessment of the resume",
  "strengths": ["short bullet", "short bullet", "short bullet"],
  "weaknesses": ["short bullet", "short bullet", "short bullet"],
  "improvement_suggestions": ["specific actionable suggestion", "specific actionable suggestion", "specific actionable suggestion", "specific actionable suggestion"],
  "rewrite_examples": [
    {{"original": "a weak bullet point pulled from the resume", "improved": "a stronger rewritten version using metrics/action verbs"}}
  ]
}}
"""


def generate_ai_feedback(resume_text: str, job_role: str, missing_required: list, missing_preferred: list) -> dict:
    """Returns structured feedback dict. Falls back to a rule-based stub if no API key is set."""
    prompt = PROMPT_TEMPLATE.format(
        job_role=job_role,
        resume_text=resume_text[:6000],  # keep prompt reasonably sized
        missing_required=", ".join(missing_required) or "none",
        missing_preferred=", ".join(missing_preferred) or "none",
    )

    if config.LLM_PROVIDER == "gemini" and config.GEMINI_API_KEY:
        return _call_gemini(prompt)
    elif config.LLM_PROVIDER == "openai" and config.OPENAI_API_KEY:
        return _call_openai(prompt)
    else:
        return _fallback_feedback(missing_required, missing_preferred)


def _call_openai(prompt: str) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    try:
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        content = response.choices[0].message.content
        return _safe_parse_json(content)
    except Exception as e:
        return _fallback_feedback([], [], error=str(e))


def _call_gemini(prompt: str) -> dict:
    import google.generativeai as genai
    genai.configure(api_key=config.GEMINI_API_KEY)
    try:
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        response = model.generate_content(prompt)
        return _safe_parse_json(response.text)
    except Exception as e:
        return _fallback_feedback([], [], error=str(e))


def _safe_parse_json(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return _fallback_feedback([], [], error="Could not parse AI response as JSON.")


def _fallback_feedback(missing_required: list, missing_preferred: list, error: str = None) -> dict:
    """Used when no API key is configured, or the API call fails, so the app
    still works end-to-end without external dependencies."""
    note = " (AI provider not configured — showing rule-based feedback.)"
    if error:
        note = f" (AI call failed: {error} — showing rule-based feedback.)"

    suggestions = [
        "Add measurable outcomes (%, $, time saved) to bullet points describing your work.",
        "Start each bullet with a strong action verb (e.g., Built, Led, Optimized).",
        "Keep the resume to 1-2 pages and use consistent section headers (Experience, Education, Skills, Projects).",
    ]
    if missing_required:
        suggestions.append(
            f"Consider adding or highlighting experience with: {', '.join(missing_required)}."
        )

    return {
        "summary": "Automated rule-based review generated" + note,
        "strengths": ["Resume text was successfully extracted and parsed."],
        "weaknesses": ["Detailed AI-based qualitative review is unavailable without a configured API key."],
        "improvement_suggestions": suggestions,
        "rewrite_examples": [],
    }
