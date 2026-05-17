from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings:
    APP_TITLE: str = "Action Item Extractor"
    APP_VERSION: str = "0.1.0"
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mistral-nemo:12b")
    DB_PATH: Path = BASE_DIR / "data" / os.getenv("DB_NAME", "app.db")
    DATA_DIR: Path = BASE_DIR / "data"
    FRONTEND_DIR: Path = BASE_DIR / "frontend"


@lru_cache
def get_settings() -> Settings:
    return Settings()
