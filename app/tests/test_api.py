from fastapi.testclient import TestClient
import pytest

def test_read_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Welcome to the AI-Powered Student Counseling Platform API" in response.json()["message"]

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok" 