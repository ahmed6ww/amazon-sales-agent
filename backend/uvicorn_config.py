"""
Uvicorn configuration with extended timeout for long-running background jobs.

Usage:
    python uvicorn_config.py

This configuration:
- Sets timeout_keep_alive to 18000 seconds (5 hours)
- Enables auto-reload for development
- Configures proper logging
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development)
        timeout_keep_alive=18000,  # 5 hours (18000 seconds) for background jobs
        timeout_graceful_shutdown=30,
        log_level="info",
        access_log=True,
    )

