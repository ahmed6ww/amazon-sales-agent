from fastapi import APIRouter
from app.services.amazon.scrapper import run_spider
from pydantic import BaseModel
import asyncio

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str

@router.post("/scrape")
async def scrape_url(request: ScrapeRequest):
    """
    Scrapes a given URL and returns the extracted data.
    """
    try:
        # Running the spider in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, run_spider, request.url)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
