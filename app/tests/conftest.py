import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
from dotenv import load_dotenv

# Load .env.test if it exists
if os.path.exists('.env.test'):
    load_dotenv('.env.test')
else:
    load_dotenv()  # Fall back to regular .env

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client 