import os
from typing import Dict, Any

try:
    from firecrawl import Firecrawl
except Exception:  # pragma: no cover
    Firecrawl = None  # type: ignore


class FirecrawlClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise RuntimeError("FIRECRAWL_API_KEY is not set")
        if Firecrawl is None:
            raise RuntimeError("firecrawl-py is not installed")
        self.client = Firecrawl(api_key=self.api_key)

    def scrape(self, url: str) -> Dict[str, Any]:
        # Fetch both markdown and html to increase chance of structured extraction
        response = self.client.scrape(url, formats=["markdown", "html"])  # type: ignore
        
        # Handle the response from Firecrawl SDK
        if hasattr(response, 'success'):
            # This is a response object with success/data attributes
            if not response.success:
                return {
                    "success": False,
                    "data": {},
                    "error": getattr(response, 'error', 'Unknown error')
                }
            
            # Extract data from the response
            data = getattr(response, 'data', {})
            return {
                "success": True,
                "data": {
                    "markdown": getattr(data, 'markdown', ''),
                    "html": getattr(data, 'html', ''),
                    "metadata": getattr(data, 'metadata', {})
                }
            }
        elif isinstance(response, dict):
            # Direct dictionary response
            return response
        else:
            # Handle unexpected response format
            return {
                "success": True,
                "data": {
                    "markdown": str(response) if response else '',
                    "html": '',
                    "metadata": {}
                }
            } 