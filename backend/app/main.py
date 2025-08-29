from fastapi import FastAPI
from app.api.v1.endpoints import upload, scraper

app = FastAPI(
    title="Amazon Sales Agent API",
    description="API for managing and interacting with sales agents.",
    version="0.1.0"
)

# Include the router from the upload endpoint
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(scraper.router, prefix="/api/v1", tags=["scraper"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Amazon Sales Agent API"}
