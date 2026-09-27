from datetime import date
from typing import Any

from backend.graph.state import TripState

TASKS = [
    "Search mock flights and hotels",
    "Retrieve visa and destination guidance from the RAG knowledge base",
    "Search current events, festivals, closures and travel advisories with Tavily",
    "Get date-aware weather from Open-Meteo",
    "Create a day-by-day itinerary using retrieved context and weather",
    "Calculate all trip costs and check the budget",
]


def planner(state: TripState) -> dict[str, Any]:
    duration = (date.fromisoformat(state["end_date"]) - date.fromisoformat(state["start_date"])).days
    attempt = state.get("planning_attempts", 0) + int(state.get("budget_checked", False))
    strategy = "Choose a balanced plan."
    if attempt == 1:
        strategy = "Re-plan: choose the lowest-priced available mock flight and hotel, and prioritize free activities."
    elif attempt >= 2:
        strategy = "Re-plan for minimum cost: choose the lowest-priced mock flight and hotel and use free indoor/outdoor activities."
    return {
        "duration": duration,
        "execution_plan": TASKS + [strategy],
        "planning_attempts": attempt,
        "budget_checked": False,
    }
