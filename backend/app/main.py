from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import upload, test_research_keywords, background_jobs
from app.core.config import settings
import logging

# Configure logging to show INFO level logs with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output to console
    ]
)

# Set httpx to WARNING to reduce noise from API calls
logging.getLogger("httpx").setLevel(logging.WARNING)

app = FastAPI(
    title="Amazon Sales Intelligence API",
    description="AI-powered Amazon product analysis and optimization platform. Complete pipeline for research, keyword analysis, scoring, and SEO optimization.",
    version="1.0"
)

# Add CORS middleware for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the production endpoints only
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(test_research_keywords.router, prefix="/api/v1", tags=["amazon-sales-intelligence"])
app.include_router(background_jobs.router, prefix="/api/v1", tags=["background-jobs"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Amazon Sales Agent API"}
