"""
Core configuration settings for the Amazon Sales Agent Backend
"""

import os
from typing import Optional

class Settings:
    """Application settings from environment variables"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    
    # Agent Configuration
    USE_AI_AGENTS: bool = os.getenv("USE_AI_AGENTS", "true").lower() == "true"
    FALLBACK_TO_DIRECT: bool = os.getenv("FALLBACK_TO_DIRECT", "true").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,https://amazon-sales-agent.vercel.app,https://amazon-sales-agent.onrender.com"
    )
    
    # API Configuration
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "300"))  # 5 minutes default
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    @property
    def openai_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        return self.OPENAI_API_KEY is not None and self.OPENAI_API_KEY.strip() != ""
    
    def get_cors_origins(self) -> list[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

# Global settings instance
settings = Settings() 