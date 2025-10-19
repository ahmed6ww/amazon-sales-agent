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
        # Load .env file first
        load_dotenv(find_dotenv(), override=True)
        
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
        self.API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "600"))  # 10 minutes for large keyword processing
        self.MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
        
        # Multi-Batch Processing Configuration
        self.BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "25"))  # Small batches to prevent timeouts
        self.MAX_CONCURRENT_BATCHES: int = int(os.getenv("MAX_CONCURRENT_BATCHES", "3"))  # Limit concurrent processing
        self.BATCH_TIMEOUT: int = int(os.getenv("BATCH_TIMEOUT", "120"))  # 2 minutes per batch
        self.ENABLE_FALLBACK_PROCESSING: bool = os.getenv("ENABLE_FALLBACK_PROCESSING", "true").lower() == "true"
        
        # Rate Limiting Configuration
        self.OPENAI_REQUESTS_PER_MINUTE: int = int(os.getenv("OPENAI_REQUESTS_PER_MINUTE", "15"))
        self.OPENAI_REQUESTS_PER_SECOND: int = int(os.getenv("OPENAI_REQUESTS_PER_SECOND", "2"))
        self.OPENAI_MAX_RETRIES: int = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
        self.OPENAI_BASE_RETRY_DELAY: float = float(os.getenv("OPENAI_BASE_RETRY_DELAY", "1.0"))
        
        # Monitoring Configuration
        self.ENABLE_OPENAI_MONITORING: bool = os.getenv("ENABLE_OPENAI_MONITORING", "true").lower() == "true"
        self.LOG_DETAILED_STATS: bool = os.getenv("LOG_DETAILED_STATS", "true").lower() == "true"
        
        # Keyword Processing Configuration
        # Batch size for root extraction and keyword processing
        # Higher values = faster processing but more memory usage
        # Recommended: 500-1000 for optimal balance
        self.KEYWORD_BATCH_SIZE: int = int(os.getenv("KEYWORD_BATCH_SIZE", "500"))

        # Logging Configuration
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "WARNING")  # Changed from INFO to WARNING
        self.DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"

        # Research/CSV Configuration
        # Global top-N limit applied consistently across CSV sampling and code-based relevancy logic
        # Used by research agent prompt context and internal computations
        # Increased default to handle larger keyword lists with root-based optimization
        self.RESEARCH_CSV_TOP_N = int(os.getenv("RESEARCH_CSV_TOP_N", "50"))

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