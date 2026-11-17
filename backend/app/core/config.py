from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'cpu_scheduler.db'}")
MODEL_DIR = Path(os.getenv("MODEL_DIR", BASE_DIR / "storage/models"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "storage/uploads"))
CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()]

MODEL_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
