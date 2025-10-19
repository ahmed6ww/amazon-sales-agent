"""
Background Job Endpoints - Non-blocking analysis with status polling
Solves the 500 timeout error by returning job_id immediately
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import Optional
import logging

from app.services.job_manager import JobManager
from app.api.v1.endpoints.test_research_keywords import amazon_sales_intelligence_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()


async def run_pipeline_in_background(
    job_id: str,
    asin_or_url: str,
    marketplace: str,
    main_keyword: Optional[str],
    revenue_csv_content: bytes,
    revenue_csv_filename: str,
    design_csv_content: bytes,
    design_csv_filename: str
):
    """
    Run the pipeline in background and save results.
    
    Args:
        job_id: Unique job identifier
        asin_or_url: Amazon ASIN or URL
        marketplace: Marketplace code
        main_keyword: Optional main keyword
        revenue_csv_content: Revenue CSV file content
        revenue_csv_filename: Revenue CSV filename
        design_csv_content: Design CSV file content
        design_csv_filename: Design CSV filename
    """
    try:
        logger.info(f"🚀 [BACKGROUND JOB] Starting job: {job_id}")
        JobManager.update_status(job_id, "processing", progress=5, message="Starting pipeline...")
        
        # Create temporary UploadFile objects from bytes
        from tempfile import SpooledTemporaryFile
        
        # Create SpooledTemporaryFile objects (more robust than BytesIO)
        revenue_file = SpooledTemporaryFile(max_size=1024*1024*50)  # 50MB threshold
        revenue_file.write(revenue_csv_content)
        revenue_file.seek(0)
        
        design_file = SpooledTemporaryFile(max_size=1024*1024*50)  # 50MB threshold
        design_file.write(design_csv_content)
        design_file.seek(0)
        
        revenue_csv = UploadFile(
            file=revenue_file,
            filename=revenue_csv_filename
        )
        design_csv = UploadFile(
            file=design_file,
            filename=design_csv_filename
        )
        
        # Update status
        JobManager.update_status(job_id, "processing", progress=10, message="Scraping product...")
        
        # Run the actual pipeline
        result = await amazon_sales_intelligence_pipeline(
            asin_or_url=asin_or_url,
            marketplace=marketplace,
            main_keyword=main_keyword,
            revenue_csv=revenue_csv,
            design_csv=design_csv
        )
        
        # Save results
        JobManager.save_results(job_id, result)
        JobManager.update_status(job_id, "complete", progress=100, message="Pipeline completed successfully")
        
        logger.info(f"✅ [BACKGROUND JOB] Job completed: {job_id}")
        
    except Exception as e:
        logger.error(f"❌ [BACKGROUND JOB] Job failed: {job_id} - {str(e)}", exc_info=True)
        JobManager.mark_failed(job_id, str(e))


@router.post("/start-analysis")
async def start_analysis(
    background_tasks: BackgroundTasks,
    asin_or_url: str = Form(...),
    marketplace: str = Form("US"),
    main_keyword: Optional[str] = Form(None),
    revenue_csv: Optional[UploadFile] = File(None),
    design_csv: Optional[UploadFile] = File(None),
):
    """
    Start analysis in background and return job_id immediately.
    
    This endpoint returns instantly (~1 second) and processes the pipeline in background.
    Use /job-status/{job_id} to check progress and /job-results/{job_id} to get results.
    
    Returns:
        {
            "job_id": "abc-123-def",
            "status": "processing",
            "message": "Job started successfully. Use /job-status/{job_id} to check progress."
        }
    """
    try:
        # Validate inputs
        if not asin_or_url.strip():
            raise HTTPException(status_code=400, detail="asin_or_url is required")
        
        if not revenue_csv or not design_csv:
            raise HTTPException(status_code=400, detail="Both revenue_csv and design_csv are required")
        
        # Create job
        job_id = JobManager.create_job()
        
        # Read CSV files into memory (so we can pass to background task)
        revenue_content = await revenue_csv.read()
        design_content = await design_csv.read()
        
        # Schedule background task
        background_tasks.add_task(
            run_pipeline_in_background,
            job_id=job_id,
            asin_or_url=asin_or_url,
            marketplace=marketplace,
            main_keyword=main_keyword,
            revenue_csv_content=revenue_content,
            revenue_csv_filename=revenue_csv.filename,
            design_csv_content=design_content,
            design_csv_filename=design_csv.filename
        )
        
        logger.info(f"✅ [API] Job started: {job_id}")
        
        return {
            "job_id": job_id,
            "status": "processing",
            "message": f"Job started successfully. Use GET /job-status/{job_id} to check progress."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [API] Failed to start job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start job: {str(e)}")


@router.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get current status of a background job.
    
    Returns:
        {
            "job_id": "abc-123-def",
            "status": "processing" | "complete" | "failed",
            "progress": 0-100,
            "message": "Current status message",
            "created_at": "2025-01-01T12:00:00",
            "updated_at": "2025-01-01T12:05:00",
            "completed_at": "2025-01-01T12:15:00" | null,
            "error": null | "Error message"
        }
    """
    job_data = JobManager.get_job(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return job_data


@router.get("/job-results/{job_id}")
async def get_job_results(job_id: str):
    """
    Get results of a completed background job.
    
    Returns:
        Full pipeline results (same format as /amazon-sales-intelligence endpoint)
    """
    # Check job status first
    job_data = JobManager.get_job(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if job_data["status"] == "processing":
        raise HTTPException(
            status_code=202,  # Accepted but not ready
            detail="Job is still processing. Check /job-status/{job_id} for progress."
        )
    
    if job_data["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail=f"Job failed: {job_data.get('error', 'Unknown error')}"
        )
    
    # Get results
    results = JobManager.get_results(job_id)
    
    if not results:
        raise HTTPException(status_code=404, detail=f"Results not found for job {job_id}")
    
    return results

