"""Application configuration and environment variable management."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RUNBOOKS_DIR = PROJECT_ROOT / "src" / "data" / "runbooks"

# Load .env file from project root if present
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


class Settings:
    """Application settings loaded from environment or defaults."""

    def __init__(self) -> None:
        self.reload()

    def reload(self) -> None:
        """Reload settings from current environment variables."""
        # Groq settings
        self.groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY", "").strip() or None
        self.groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        self.groq_base_url: str = os.getenv(
            "GROQ_BASE_URL", "https://api.groq.com/openai/v1"
        ).strip()

        # Hindsight settings
        self.hindsight_api_key: Optional[str] = (
            os.getenv("HINDSIGHT_API_KEY", "").strip() or None
        )
        self.hindsight_api_url: str = os.getenv(
            "HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io"
        ).strip()
        self.hindsight_bank_id: str = os.getenv(
            "HINDSIGHT_BANK_ID", "incidentmind-demo"
        ).strip()

        # Application settings
        self.environment: str = os.getenv("ENVIRONMENT", "development").strip()
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").strip()
        
        db_path_str = os.getenv("DATABASE_PATH", str(DATA_DIR / "incidents.db"))
        self.database_path: Path = Path(db_path_str)
        if not self.database_path.is_absolute():
            self.database_path = PROJECT_ROOT / self.database_path

        self.runbooks_dir: Path = RUNBOOKS_DIR

    @property
    def is_groq_configured(self) -> bool:
        """Check if Groq API key is present."""
        return bool(self.groq_api_key)

    @property
    def is_hindsight_configured(self) -> bool:
        """Check if Hindsight API key is present."""
        return bool(self.hindsight_api_key)

    def set_groq_api_key(self, api_key: str) -> None:
        """Dynamically update the Groq API key."""
        clean_key = api_key.strip()
        self.groq_api_key = clean_key or None
        if clean_key:
            os.environ["GROQ_API_KEY"] = clean_key
        elif "GROQ_API_KEY" in os.environ:
            del os.environ["GROQ_API_KEY"]

    def set_hindsight_api_key(self, api_key: str) -> None:
        """Dynamically update the Hindsight API key."""
        clean_key = api_key.strip()
        self.hindsight_api_key = clean_key or None
        if clean_key:
            os.environ["HINDSIGHT_API_KEY"] = clean_key
        elif "HINDSIGHT_API_KEY" in os.environ:
            del os.environ["HINDSIGHT_API_KEY"]

    def set_hindsight_bank_id(self, bank_id: str) -> None:
        """Dynamically update the Hindsight memory bank ID."""
        clean_id = bank_id.strip() or "incidentmind-demo"
        self.hindsight_bank_id = clean_id
        os.environ["HINDSIGHT_BANK_ID"] = clean_id


# Global singleton instance
settings = Settings()
