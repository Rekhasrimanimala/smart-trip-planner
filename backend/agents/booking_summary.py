from typing import Any

from backend.graph.state import TripState

VISA_WARNING = "Visa requirements can change. Please verify the latest requirements with the relevant official embassy or immigration website before travelling."
PRICE_WARNING = "Flight and hotel prices are indicative and may change. Please verify prices before booking."


def booking_summary(state: TripState) -> dict[str, Any]:
    warnings = list(dict.fromkeys(state.get("warnings", [])))
    warnings.extend([VISA_WARNING, PRICE_WARNING])
    if not state.get("budget_met", False):
        warnings.append("The requested budget could not be met after 3 planning attempts; this is the closest available estimate.")
    summary = {
        "trip_summary": {
            "destination": state["destination"],
            "origin": state["origin"],
            "start_date": state["start_date"],
            "end_date": state["end_date"],
            "duration_days": state["duration"],
            "travelers": state["travelers"],
            "budget": state["budget"],
            "currency": state["currency"],
        },
        "flights": state.get("flights", []),
        "hotels": state.get("hotels", []),
        "selected_flight": state.get("selected_flight"),
        "selected_hotel": state.get("selected_hotel"),
        "weather": state.get("weather_summary", {"location": state["destination"], "days": state.get("weather", [])}),
        "visa": {"information": state.get("visa_info", "Not available."), "sources": state.get("visa_sources", [])},
        "events": state.get("events", []),
        "festivals": state.get("festivals", []),
        "closures": state.get("closures", []),
        "advisories": state.get("advisories", []),
        "itinerary": state.get("itinerary", []),
        "budget_breakdown": {
            "flights": state.get("flight_cost", 0),
            "hotels": state.get("hotel_cost", 0),
            "food": state.get("food_cost", 0),
            "transport": state.get("transport_cost", 0),
            "activities": state.get("activity_cost", 0),
            "total": state.get("total_cost", 0),
            "budget": state["budget"],
            "remaining": state.get("remaining_budget", 0),
            "currency": state["currency"],
            "budget_met": state.get("budget_met", False),
        },
        "planning_attempts": state.get("planning_attempts", 0),
        "warnings": warnings,
        "errors": state.get("errors", []),
    }
    return {"summary": summary}
