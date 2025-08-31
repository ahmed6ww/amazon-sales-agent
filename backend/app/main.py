import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import upload, scraper, test, analyze

app = FastAPI(
    title="Amazon Sales Agent API",
    description="API for managing and interacting with sales agents.",
    version="0.1.0"
)

# Configure CORS origins from environment variables
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", 
    "http://localhost:3000,https://amazon-sales-agent.vercel.app,https://amazon-sales-agent.onrender.com"
).split(",")

# Add CORS middleware for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router from the upload endpoint
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(scraper.router, prefix="/api/v1", tags=["scraper"])
app.include_router(test.router, prefix="/api/v1", tags=["test"])
app.include_router(analyze.router, prefix="/api/v1", tags=["analyze"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Amazon Sales Agent API"}
