"""
Central configuration loaded from environment variables (.env).
"""
import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

DB_PATH = os.getenv("DB_PATH", "data/resume_analyzer.db")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JOB_ROLES_PATH = os.path.join(BASE_DIR, "data", "job_roles.json")
SKILLS_DB_PATH = os.path.join(BASE_DIR, "data", "skills_db.json")
