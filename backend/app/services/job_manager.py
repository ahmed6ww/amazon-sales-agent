"""
Job Manager - Background job tracking and storage with Redis (Upstash) support
Handles long-running tasks with status updates and result storage.

Storage Strategy:
- Primary: Redis (Upstash) for production/deployment
- Fallback: File-based storage for local development
"""
import json
import uuid
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# REDIS CLIENT SETUP (Upstash)
# ============================================================================
redis_client = None
use_redis = False

if settings.USE_REDIS_FOR_JOBS and settings.UPSTASH_REDIS_URL and settings.UPSTASH_REDIS_TOKEN:
    try:
        from upstash_redis import Redis
        
        redis_client = Redis(
            url=settings.UPSTASH_REDIS_URL,
            token=settings.UPSTASH_REDIS_TOKEN
        )
        
        # Test connection
        redis_client.ping()
        use_redis = True
        logger.info("🔴 [JOB MANAGER] Redis (Upstash) initialized successfully")
        logger.info(f"   ⏱️  Job TTL: {settings.JOB_TTL_HOURS} hours")
    except Exception as e:
        logger.warning(f"⚠️  [JOB MANAGER] Redis connection failed: {e}")
        logger.warning(f"   📁 Falling back to file-based storage")
        use_redis = False
else:
    logger.info("📁 [JOB MANAGER] Using file-based storage (Redis not configured)")

# ============================================================================
# FILE-BASED STORAGE FALLBACK
# ============================================================================
JOBS_DIR = Path("jobs")
if not use_redis:
    JOBS_DIR.mkdir(exist_ok=True)
    logger.info(f"📁 [JOB MANAGER] Initialized job storage directory: {JOBS_DIR.absolute()}")
    if JOBS_DIR.exists():
        logger.info(f"   ✅ Directory exists and is accessible")
        # Check if directory is writable
        test_file = JOBS_DIR / ".test_write"
        try:
            test_file.write_text("test")
            test_file.unlink()
            logger.info(f"   ✅ Directory is writable")
        except Exception as e:
            logger.error(f"   ❌ Directory is NOT writable: {e}")
    else:
        logger.error(f"   ❌ Directory does not exist after mkdir()")


class JobManager:
    """Manages background jobs with Redis (Upstash) or file-based storage."""
    
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
        logger.info(f"✅ [JOB MANAGER] Created job: {job_id} (storage: {'Redis' if use_redis else 'File'})")
        
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
        if use_redis:
            JobManager._save_results_redis(job_id, results)
        else:
            JobManager._save_results_file(job_id, results)
    
    @staticmethod
    def get_job(job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job data dictionary or None if not found
        """
        if use_redis:
            return JobManager._get_job_redis(job_id)
        else:
            return JobManager._get_job_file(job_id)
    
    @staticmethod
    def get_results(job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job results.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Results dictionary or None if not found
        """
        if use_redis:
            return JobManager._get_results_redis(job_id)
        else:
            return JobManager._get_results_file(job_id)
    
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
    
    # ========================================================================
    # REDIS IMPLEMENTATION
    # ========================================================================
    
    @staticmethod
    def _save_job(job_id: str, job_data: Dict[str, Any]):
        """Save job data to Redis or file."""
        if use_redis:
            JobManager._save_job_redis(job_id, job_data)
        else:
            JobManager._save_job_file(job_id, job_data)
    
    @staticmethod
    def _save_job_redis(job_id: str, job_data: Dict[str, Any]):
        """Save job data to Redis with TTL."""
        try:
            key = f"job:{job_id}"
            ttl_seconds = settings.JOB_TTL_HOURS * 3600
            
            redis_client.set(key, json.dumps(job_data))
            redis_client.expire(key, ttl_seconds)
            
            logger.debug(f"💾 [REDIS] Saved job: {job_id} (TTL: {settings.JOB_TTL_HOURS}h)")
        except Exception as e:
            logger.error(f"❌ [REDIS] Failed to save job {job_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def _get_job_redis(job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data from Redis."""
        try:
            key = f"job:{job_id}"
            data = redis_client.get(key)
            
            if data is None:
                logger.debug(f"🔍 [REDIS] Job not found: {job_id}")
                return None
            
            return json.loads(data)
        except Exception as e:
            logger.error(f"❌ [REDIS] Failed to load job {job_id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _save_results_redis(job_id: str, results: Dict[str, Any]):
        """Save job results to Redis with TTL."""
        try:
            key = f"results:{job_id}"
            ttl_seconds = settings.JOB_TTL_HOURS * 3600
            
            results_json = json.dumps(results)
            results_size = len(results_json)
            
            logger.info(f"📁 [REDIS] Saving results for: {job_id}")
            logger.info(f"📊 [REDIS] Results size: {results_size} bytes ({results_size / 1024:.1f} KB)")
            
            redis_client.set(key, results_json)
            redis_client.expire(key, ttl_seconds)
            
            # Verify by reading back
            verify = redis_client.get(key)
            if verify is not None:
                logger.info(f"💾 [REDIS] ✅ Results saved successfully for job: {job_id}")
                logger.info(f"   💽 Size: {results_size / 1024:.1f} KB")
                logger.info(f"   ⏱️  TTL: {settings.JOB_TTL_HOURS} hours")
            else:
                logger.error(f"❌ [REDIS] Verification failed: Results not found after save")
                raise Exception("Results not found after Redis save")
        except Exception as e:
            logger.error(f"❌ [REDIS] Failed to save results for {job_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def _get_results_redis(job_id: str) -> Optional[Dict[str, Any]]:
        """Get job results from Redis."""
        try:
            key = f"results:{job_id}"
            
            logger.info(f"📂 [REDIS] Retrieving results for job: {job_id}")
            
            data = redis_client.get(key)
            
            if data is None:
                logger.warning(f"⚠️  [REDIS] Results not found for job: {job_id}")
                # List all keys for debugging
                try:
                    all_keys = redis_client.keys(f"*{job_id}*")
                    if all_keys:
                        logger.warning(f"   📁 Found related keys: {all_keys}")
                    else:
                        logger.warning(f"   📁 No keys found matching: *{job_id}*")
                except Exception:
                    pass
                return None
            
            results_size = len(data)
            logger.info(f"   ✅ Results found: {results_size / 1024:.1f} KB")
            
            results = json.loads(data)
            logger.info(f"✅ [REDIS] Results loaded successfully for job: {job_id}")
            
            return results
        except Exception as e:
            logger.error(f"❌ [REDIS] Failed to load results for {job_id}: {e}", exc_info=True)
            return None
    
    # ========================================================================
    # FILE-BASED IMPLEMENTATION (Fallback)
    # ========================================================================
    
    @staticmethod
    def _save_job_file(job_id: str, job_data: Dict[str, Any]):
        """Save job data to file."""
        job_file = JOBS_DIR / f"{job_id}.json"
        try:
            with open(job_file, "w") as f:
                json.dump(job_data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ [FILE] Failed to save job {job_id}: {e}")
    
    @staticmethod
    def _get_job_file(job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data from file."""
        job_file = JOBS_DIR / f"{job_id}.json"
        if not job_file.exists():
            return None
        
        try:
            with open(job_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ [FILE] Failed to load job {job_id}: {e}")
            return None
    
    @staticmethod
    def _save_results_file(job_id: str, results: Dict[str, Any]):
        """Save job results to file."""
        results_file = JOBS_DIR / f"{job_id}_results.json"
        try:
            logger.info(f"📁 [FILE] Saving results to: {results_file.absolute()}")
            logger.info(f"📊 [FILE] Results size: {len(str(results))} bytes")
            
            with open(results_file, "w") as f:
                json.dump(results, f, indent=2)
            
            # Verify file was written
            if results_file.exists():
                file_size = results_file.stat().st_size
                logger.info(f"💾 [FILE] ✅ Results saved successfully for job: {job_id}")
                logger.info(f"   📄 File: {results_file.absolute()}")
                logger.info(f"   💽 Size: {file_size / 1024:.1f} KB")
            else:
                logger.error(f"❌ [FILE] File not found after write: {results_file}")
                raise Exception("Results file not found after write")
        except Exception as e:
            logger.error(f"❌ [FILE] Failed to save results for {job_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def _get_results_file(job_id: str) -> Optional[Dict[str, Any]]:
        """Get job results from file."""
        results_file = JOBS_DIR / f"{job_id}_results.json"
        
        logger.info(f"📂 [FILE] Retrieving results for job: {job_id}")
        logger.info(f"   📄 Looking for file: {results_file.absolute()}")
        
        if not results_file.exists():
            logger.warning(f"⚠️  [FILE] Results file not found: {results_file.absolute()}")
            logger.warning(f"   📁 Jobs directory contents:")
            try:
                for file in JOBS_DIR.glob("*"):
                    logger.warning(f"      - {file.name}")
            except Exception as list_err:
                logger.warning(f"      Failed to list directory: {list_err}")
            return None
        
        try:
            file_size = results_file.stat().st_size
            logger.info(f"   ✅ File exists: {file_size / 1024:.1f} KB")
            
            with open(results_file, "r") as f:
                results = json.load(f)
            
            logger.info(f"✅ [FILE] Results loaded successfully for job: {job_id}")
            return results
        except Exception as e:
            logger.error(f"❌ [FILE] Failed to load results for {job_id}: {e}", exc_info=True)
            return None
    
    # ========================================================================
    # CLEANUP (File-based only)
    # ========================================================================
    
    @staticmethod
    def cleanup_old_jobs(days: int = 7):
        """
        Clean up jobs older than specified days.
        Only applies to file-based storage (Redis uses TTL).
        
        Args:
            days: Age threshold in days
        """
        if use_redis:
            logger.info("🔴 [JOB MANAGER] Using Redis - cleanup handled by TTL")
            return
        
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
                    logger.error(f"❌ [FILE] Failed to delete {job_file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"🗑️  [FILE] Cleaned up {deleted_count} old jobs")
