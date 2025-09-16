from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import upload, test_research_keywords
from app.core.config import settings

app = FastAPI(
    title="Amazon Sales Agent API",
    description="API for managing and interacting with sales agents.",
    version="1"
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
app.include_router(test_research_keywords.router, prefix="/api/v1", tags=["production"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Amazon Sales Agent API"}
