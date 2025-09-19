import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_root_redirect():
    """Test root endpoint redirects to dashboard."""
    response = client.get("/")
    assert response.status_code == 200  # SPA should serve index.html

def test_api_docs():
    """Test API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200






