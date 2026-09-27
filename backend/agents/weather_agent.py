from datetime import date
from typing import Any

from backend.graph.state import TripState
from backend.services.weather_service import get_weather


async def weather_agent(state: TripState) -> dict[str, Any]:
    result = await get_weather(
        state["destination"], date.fromisoformat(state["start_date"]), date.fromisoformat(state["end_date"])
    )
    warnings = list(state.get("warnings", []))
    errors = list(state.get("errors", []))
    if result.get("error"):
        warnings.append(result["error"])
    itinerary = [dict(day) for day in state.get("itinerary", [])]
    for day in itinerary:
        forecast = next((item for item in result.get("days", []) if item.get("date") == day.get("date")), None)
        if forecast and ((forecast.get("weather_code") or 0) >= 51 or (forecast.get("precipitation_probability") or 0) >= 55):
            day["weather_note"] = "Rain is possible; confirm conditions and keep an indoor alternative."
            for slot in ("morning", "afternoon"):
                activity = str(day.get(slot, ""))
                if any(token in activity.casefold() for token in ("walk", "viewpoint", "waterfront", "garden")):
                    day[slot] = "Indoor museum, gallery or covered market; confirm current opening hours"
    return {
        "weather": result.get("days", []),
        "weather_summary": result,
        "itinerary": itinerary,
        "warnings": warnings,
        "errors": errors,
    }
