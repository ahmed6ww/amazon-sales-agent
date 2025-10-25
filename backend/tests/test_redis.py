"""Redis connection and job storage tests."""

import pytest
import os


def test_redis_env_vars():
    """Test that Redis environment variables are set."""
    # In CI, these should be set as secrets
    # In local testing, they can be None (will fall back to file storage)
    redis_url = os.getenv("UPSTASH_REDIS_URL")
    redis_token = os.getenv("UPSTASH_REDIS_TOKEN")
    
    if redis_url and redis_token:
        assert redis_url.startswith("https://"), "Redis URL should be HTTPS"
        assert len(redis_token) > 20, "Redis token should be substantial"


@pytest.mark.skipif(
    not os.getenv("UPSTASH_REDIS_URL") or not os.getenv("UPSTASH_REDIS_TOKEN"),
    reason="Redis credentials not available",
)
def test_redis_connection():
    """Test actual Redis connection (only if credentials available)."""
    from app.services.job_manager import JobManager
    
    # Try to create a test job
    job_id = JobManager.create_job("test", {"test": "data"})
    assert job_id is not None
    
    # Try to retrieve it
    job_data = JobManager.get_job(job_id)
    assert job_data is not None
    assert job_data["status"] == "pending"

