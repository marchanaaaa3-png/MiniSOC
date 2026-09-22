from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent


class Config:
    # Flask secret key
    SECRET_KEY = "minisoc-development-secret-key"

    # SQLite database location
    DATABASE_PATH = BASE_DIR / "data" / "minisoc.db"