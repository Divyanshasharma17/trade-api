from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

GEMINI_MODEL = "models/gemini-2.0-flash-lite"
VALID_SECTORS = [
    "pharmaceuticals",
    "technology",
    "agriculture",
    "textiles",
    "automobiles",
    "energy",
    "finance",
    "healthcare",
    "manufacturing",
    "retail",
    "telecommunications",
    "chemicals",
]

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing from .env file!")
if not SECRET_KEY:
    raise ValueError("❌ SECRET_KEY is missing from .env file!")