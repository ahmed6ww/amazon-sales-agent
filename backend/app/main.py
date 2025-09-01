from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import upload, test, analyze, test_research, scrape_mvp
from app.core.config import settings

app = FastAPI(
    title="Amazon Sales Agent API",
    description="API for managing and interacting with sales agents.",
    version="0.1.0"
)

# Add CORS middleware for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers from all endpoints
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(test.router, prefix="/api/v1", tags=["test"])
app.include_router(analyze.router, prefix="/api/v1", tags=["analyze"])
app.include_router(test_research.router, prefix="/api/v1", tags=["test-research"]) 
app.include_router(scrape_mvp.router, prefix="/api/v1", tags=["scrape-mvp"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Amazon Sales Agent API"}
