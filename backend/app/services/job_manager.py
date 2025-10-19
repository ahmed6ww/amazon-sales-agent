"""
Job Manager - Background job tracking and storage
Handles long-running tasks with status updates and result storage
"""
import json
import uuid
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Job storage directory
JOBS_DIR = Path("jobs")
JOBS_DIR.mkdir(exist_ok=True)


class JobManager:
    """Manages background jobs with file-based storage."""
    
    @staticmethod
    def create_job() -> str:
        """
        Create a new job and return its ID.
        
        Returns:
            str: Unique job ID
        """
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "status": "processing",
            "progress": 0,
            "message": "Job started",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None,
            "error": None
        }
        
        # Save initial status
        JobManager._save_job(job_id, job_data)
        logger.info(f"✅ [JOB MANAGER] Created job: {job_id}")
        
        return job_id
    
    @staticmethod
    def update_status(job_id: str, status: str, progress: int = None, message: str = None):
        """
        Update job status.
        
        Args:
            job_id: Job identifier
            status: New status (processing, complete, failed)
            progress: Progress percentage (0-100)
            message: Status message
        """
        job_data = JobManager.get_job(job_id)
        if not job_data:
            logger.error(f"❌ [JOB MANAGER] Job not found: {job_id}")
            return
        
        job_data["status"] = status
        job_data["updated_at"] = datetime.now().isoformat()
        
        if progress is not None:
            job_data["progress"] = progress
        
        if message is not None:
            job_data["message"] = message
        
        if status == "complete":
            job_data["completed_at"] = datetime.now().isoformat()
            job_data["progress"] = 100
        
        JobManager._save_job(job_id, job_data)
        logger.info(f"📊 [JOB MANAGER] Updated job {job_id}: {status} ({progress}%)")
    
    @staticmethod
    def save_results(job_id: str, results: Dict[str, Any]):
        """
        Save job results.
        
        Args:
            job_id: Job identifier
            results: Results dictionary
        """
        results_file = JOBS_DIR / f"{job_id}_results.json"
        try:
            with open(results_file, "w") as f:
                json.dump(results, f, indent=2)
            logger.info(f"💾 [JOB MANAGER] Saved results for job: {job_id}")
        except Exception as e:
            logger.error(f"❌ [JOB MANAGER] Failed to save results for {job_id}: {e}")
    
    @staticmethod
    def get_job(job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job data dictionary or None if not found
        """
        job_file = JOBS_DIR / f"{job_id}.json"
        if not job_file.exists():
            return None
        
        try:
            with open(job_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ [JOB MANAGER] Failed to load job {job_id}: {e}")
            return None
    
    @staticmethod
    def get_results(job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job results.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Results dictionary or None if not found
        """
        results_file = JOBS_DIR / f"{job_id}_results.json"
        if not results_file.exists():
            return None
        
        try:
            with open(results_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ [JOB MANAGER] Failed to load results for {job_id}: {e}")
            return None
    
    @staticmethod
    def mark_failed(job_id: str, error: str):
        """
        Mark job as failed.
        
        Args:
            job_id: Job identifier
            error: Error message
        """
        job_data = JobManager.get_job(job_id)
        if not job_data:
            logger.error(f"❌ [JOB MANAGER] Job not found: {job_id}")
            return
        
        job_data["status"] = "failed"
        job_data["error"] = error
        job_data["updated_at"] = datetime.now().isoformat()
        job_data["completed_at"] = datetime.now().isoformat()
        
        JobManager._save_job(job_id, job_data)
        logger.error(f"❌ [JOB MANAGER] Job {job_id} failed: {error}")
    
    @staticmethod
    def _save_job(job_id: str, job_data: Dict[str, Any]):
        """
        Save job data to file.
        
        Args:
            job_id: Job identifier
            job_data: Job data dictionary
        """
        job_file = JOBS_DIR / f"{job_id}.json"
        try:
            with open(job_file, "w") as f:
                json.dump(job_data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ [JOB MANAGER] Failed to save job {job_id}: {e}")
    
    @staticmethod
    def cleanup_old_jobs(days: int = 7):
        """
        Clean up jobs older than specified days.
        
        Args:
            days: Age threshold in days
        """
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        for job_file in JOBS_DIR.glob("*.json"):
            if job_file.stat().st_mtime < cutoff_time:
                try:
                    job_file.unlink()
                    # Also delete results file
                    results_file = JOBS_DIR / f"{job_file.stem}_results.json"
                    if results_file.exists():
                        results_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"❌ [JOB MANAGER] Failed to delete {job_file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"🗑️  [JOB MANAGER] Cleaned up {deleted_count} old jobs")

