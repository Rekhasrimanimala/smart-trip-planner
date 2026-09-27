import json

import pytest

from backend.mcp import currency_tools
from backend.mcp.flight_tools import search_flights
from backend.mcp.hotel_tools import search_hotels


def test_search_flights_returns_mock_route():
    result = search_flights("Chennai", "Singapore", "2026-12-10")
    assert result["date"] == "2026-12-10"
    assert result["flights"]
    assert {flight["currency"] for flight in result["flights"]} == {"INR"}


def test_search_flights_returns_empty_for_unknown_route():
    assert search_flights("Unknown", "Singapore", "2026-12-10")["flights"] == []


def test_search_hotels_returns_city_mock_data():
    result = search_hotels("Singapore", "2026-12-10", "2026-12-14")
    assert result["check_in"] == "2026-12-10"
    assert result["hotels"]
    assert all("rating" in hotel and "price_per_night" in hotel for hotel in result["hotels"])


@pytest.mark.asyncio
async def test_convert_currency_same_currency_needs_no_api_call():
    result = await currency_tools.convert_currency(125, "INR", "INR")
    assert result["converted_amount"] == 125
    assert result["rate"] == 1


@pytest.mark.asyncio
async def test_convert_currency_uses_frankfurter(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"rates": {"USD": 0.012}}

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url, params):
            assert url.startswith("https://api.frankfurter.dev/")
            assert params == {"from": "INR", "to": "USD"}
            return FakeResponse()

    monkeypatch.setattr(currency_tools.httpx, "AsyncClient", FakeClient)
    result = await currency_tools.convert_currency(1000, "INR", "USD")
    assert result["converted_amount"] == 12


@pytest.mark.asyncio
async def test_convert_currency_reports_provider_errors(monkeypatch):
    class BrokenClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            raise currency_tools.httpx.ConnectError("offline")

    monkeypatch.setattr(currency_tools.httpx, "AsyncClient", BrokenClient)
    with pytest.raises(RuntimeError, match="Currency conversion unavailable"):
        await currency_tools.convert_currency(100, "INR", "USD")
