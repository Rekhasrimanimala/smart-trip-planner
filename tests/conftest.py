from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_payload() -> dict:
    start = date.today() + timedelta(days=70)
    end = start + timedelta(days=4)
    return {
        "origin": "Chennai",
        "destination": "Singapore",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "budget": 80000,
        "currency": "INR",
        "travelers": 1,
        "preferences": "Food markets and gardens",
        "passport_country": "India",
    }
