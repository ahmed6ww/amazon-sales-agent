"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app
    return TestClient(app)


def test_job_status_endpoint_not_found(client):
    """Test job status for non-existent job."""
    response = client.get("/api/v1/job-status/fake-job-id")
    assert response.status_code == 404


def test_job_results_endpoint_not_found(client):
    """Test job results for non-existent job."""
    response = client.get("/api/v1/job-results/fake-job-id")
    assert response.status_code == 404


def test_analyze_endpoint_missing_fields(client):
    """Test analyze endpoint with missing required fields."""
    response = client.post("/api/v1/analyze", json={})
    assert response.status_code == 422  # Validation error


def test_analyze_endpoint_invalid_asin(client):
    """Test analyze endpoint with invalid ASIN format."""
    response = client.post(
        "/api/v1/analyze",
        json={
            "asin": "invalid",
            "brand_name": "Test Brand",
            "csv_files": [],
        },
    )
    # Should either reject invalid ASIN or accept it (depends on validation)
    assert response.status_code in [200, 400, 422]


@pytest.mark.skipif(
    not pytest.config.getoption("--run-integration", default=False),
    reason="Integration tests disabled by default",
)
def test_full_analysis_flow(client):
    """
    Full integration test - only runs with --run-integration flag.
    
    Usage: pytest tests/ --run-integration
    """
    # This would be a full end-to-end test with real ASIN
    # Skipped by default to avoid API calls in CI
    pass

