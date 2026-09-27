from typing import Any

from langgraph.graph import END, START, StateGraph

from backend.agents.booking_summary import booking_summary
from backend.agents.budget_agent import budget_agent
from backend.agents.itinerary_agent import itinerary_agent
from backend.agents.planner import planner
from backend.agents.weather_agent import weather_agent
from backend.graph.state import TripState

MAX_PLANNING_ATTEMPTS = 3


def _after_budget(state: TripState) -> str:
    if state["total_cost"] > state["budget"] and state.get("planning_attempts", 0) < MAX_PLANNING_ATTEMPTS:
        return "planner"
    return "booking_summary"


def build_trip_graph() -> Any:
    graph = StateGraph(TripState)
    graph.add_node("planner", planner)
    graph.add_node("itinerary_agent", itinerary_agent)
    graph.add_node("weather_agent", weather_agent)
    graph.add_node("budget_agent", budget_agent)
    graph.add_node("booking_summary", booking_summary)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "itinerary_agent")
    graph.add_edge("itinerary_agent", "weather_agent")
    graph.add_edge("weather_agent", "budget_agent")
    graph.add_conditional_edges(
        "budget_agent",
        _after_budget,
        {"planner": "planner", "booking_summary": "booking_summary"},
    )
    graph.add_edge("booking_summary", END)
    return graph.compile()


async def run_trip(request: dict[str, Any]) -> dict[str, Any]:
    duration = (request["end_date"] - request["start_date"]).days
    state: TripState = {
        "user_request": request.get("user_request", ""),
        "origin": request["origin"],
        "destination": request["destination"],
        "start_date": request["start_date"].isoformat(),
        "end_date": request["end_date"].isoformat(),
        "duration": duration,
        "budget": request["budget"],
        "currency": request["currency"],
        "travelers": request["travelers"],
        "preferences": request.get("preferences", ""),
        "passport_country": request.get("passport_country", "India"),
        "execution_plan": [],
        "planning_attempts": 0,
        "flights": [],
        "hotels": [],
        "visa_info": "",
        "visa_sources": [],
        "events": [],
        "festivals": [],
        "closures": [],
        "advisories": [],
        "weather": [],
        "itinerary": [],
        "food_cost": 0.0,
        "transport_cost": 0.0,
        "activity_cost": 0.0,
        "flight_cost": 0.0,
        "hotel_cost": 0.0,
        "total_cost": 0.0,
        "remaining_budget": 0.0,
        "budget_met": False,
        "warnings": [],
        "errors": [],
        "budget_checked": False,
    }
    result = await build_trip_graph().ainvoke(state)
    return result["summary"]
