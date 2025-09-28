import os
from dotenv import load_dotenv

# Load .env from the same directory as this config file
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path, override=True)

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./smask_db.sqlite3")