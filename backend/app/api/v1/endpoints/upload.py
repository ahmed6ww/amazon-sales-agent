from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging

from app.services.file_processing.csv_processor import parse_csv_bytes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Accepts a CSV file upload, processes it, and returns the parsed data.
    """
    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")

    try:
        # Read file content as bytes
        contents = await file.read()
        
        # Process the CSV bytes using the service
        result = parse_csv_bytes(file.filename, contents)

        if not result.get("success"):
            logger.error(f"CSV parsing failed for {file.filename}: {result.get('error')}")
            raise HTTPException(status_code=500, detail=f"Failed to process CSV file: {result.get('error')}")

        logger.info(f"Successfully processed {file.filename}, found {result.get('count')} records.")
        
        # Return the parsed data
        return {
            "filename": file.filename,
            "count": result.get("count"),
            "data": result.get("data"),
        }

    except Exception as e:
        logger.exception(f"An unexpected error occurred while processing {file.filename}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

