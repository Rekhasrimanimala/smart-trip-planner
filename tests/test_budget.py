import pytest

from backend.agents.budget_agent import budget_agent
from backend.graph.trip_graph import _after_budget


@pytest.mark.asyncio
async def test_budget_calculation_uses_flight_hotel_and_daily_estimates(monkeypatch):
    import backend.agents.budget_agent as budget_module

    async def convert(amount, source, target):
        return {"converted_amount": amount}

    monkeypatch.setattr(budget_module, "convert_currency", convert)
    state = {
        "origin": "Chennai", "destination": "Singapore", "start_date": "2026-12-10",
        "end_date": "2026-12-14", "duration": 4, "budget": 100000, "currency": "INR",
        "travelers": 1, "planning_attempts": 0, "warnings": [], "errors": [],
    }
    result = await budget_agent(state)
    assert result["flight_cost"] == 50000
    assert result["hotel_cost"] == 27200
    assert result["food_cost"] == 5600
    assert result["transport_cost"] == 2400
    assert result["activity_cost"] == 4800
    assert result["total_cost"] == 90000
    assert result["remaining_budget"] == 10000


def test_budget_exceeded_condition_returns_to_planner_then_summarizes():
    assert _after_budget({"total_cost": 1200, "budget": 1000, "planning_attempts": 2}) == "planner"
    assert _after_budget({"total_cost": 1200, "budget": 1000, "planning_attempts": 3}) == "booking_summary"
    assert _after_budget({"total_cost": 900, "budget": 1000, "planning_attempts": 0}) == "booking_summary"
