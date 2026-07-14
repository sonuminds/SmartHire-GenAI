import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore"

JOBS_INDEX_PATH = VECTORSTORE_DIR / "jobs.index"
JOBS_METADATA_PATH = VECTORSTORE_DIR / "jobs_metadata.pkl"

CAREER_NOTES_DIR = DATA_DIR / "career_notes"

API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=API_KEY)