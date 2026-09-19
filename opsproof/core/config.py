"""Central, environment-backed configuration with safe local defaults."""
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = ROOT / "policies"
SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".docx"}

def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}

def _positive_int(name: str, default: int) -> int:
    try: value=int(os.getenv(name,str(default)))
    except ValueError: return default
    return value if value > 0 else default

@dataclass(frozen=True)
class Settings:
    db_path: str = os.getenv("OPSPROOF_DB_PATH", "opsproof.db")
    max_upload_bytes: int = _positive_int("OPSPROOF_MAX_UPLOAD_BYTES", 5 * 1024 * 1024)
    semantic_model: str | None = os.getenv("OPSPROOF_SEMANTIC_MODEL") or None
    enable_semantic: bool = _bool("OPSPROOF_ENABLE_SEMANTIC")
    log_level: str = os.getenv("OPSPROOF_LOG_LEVEL", "INFO").upper()

SETTINGS = Settings()
MAX_FILE_BYTES = SETTINGS.max_upload_bytes
