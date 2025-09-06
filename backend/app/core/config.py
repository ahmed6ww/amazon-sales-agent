"""
Core configuration settings for the Amazon Sales Agent Backend
"""

import os
from typing import Optional

from dotenv import find_dotenv, load_dotenv

class Settings:
    """Application settings sourced from environment variables (.env supported)."""

    def __init__(self) -> None:
        self._load_from_environment()

    def _load_from_environment(self) -> None:
        """(Re)load configuration from current environment variables."""
        # OpenAI Configuration
        self.OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")

        # Agent Configuration
        self.USE_AI_AGENTS: bool = os.getenv("USE_AI_AGENTS", "true").lower() == "true"
        self.FALLBACK_TO_DIRECT: bool = os.getenv("FALLBACK_TO_DIRECT", "true").lower() == "true"

        # CORS Configuration
        self.CORS_ORIGINS: str = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,https://amazon-sales-agent.vercel.app,https://amazon-sales-agent.onrender.com",
        )

        # API Configuration
        self.API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "300"))  # 5 minutes default
        self.MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

        # Logging Configuration
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"

        # Research/CSV Configuration
        # Global top-N limit applied consistently across CSV sampling and code-based relevancy logic
        # Used by research agent prompt context and internal computations
        self.RESEARCH_CSV_TOP_N = int(os.getenv("RESEARCH_CSV_TOP_N", "20"))

    def reload(self) -> None:
        """Reload settings from environment (and .env if changed)."""
        load_dotenv(find_dotenv(), override=True)
        self._load_from_environment()

    @property
    def openai_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        return self.OPENAI_API_KEY is not None and self.OPENAI_API_KEY.strip() != ""
    
    def get_cors_origins(self) -> list[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

# Global settings instance
settings = Settings() 