import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# Load environment variables from backend/.env or root .env
load_dotenv(BASE_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
if OPENROUTER_API_KEY.startswith('"') and OPENROUTER_API_KEY.endswith('"'):
    OPENROUTER_API_KEY = OPENROUTER_API_KEY[1:-1]

MODEL_NAME = "openai/gpt-oss-120b"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(exist_ok=True, parents=True)
DB_PATH = DB_DIR / "pm.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True, parents=True)
