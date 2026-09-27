import asyncio
from typing import Any

from backend.graph.state import TripState
from backend.mcp.currency_tools import convert_currency
from backend.mcp.flight_tools import search_flights
from backend.mcp.hotel_tools import search_hotels


async def _in_user_currency(amount: float, currency: str) -> float:
    converted = await convert_currency(amount, "INR", currency)
    return float(converted["converted_amount"])


async def budget_agent(state: TripState) -> dict[str, Any]:
    warnings = list(state.get("warnings", []))
    errors = list(state.get("errors", []))
    flight_result = search_flights(state["origin"], state["destination"], state["start_date"])
    hotel_result = search_hotels(state["destination"], state["start_date"], state["end_date"])
    flights = flight_result["flights"]
    hotels = hotel_result["hotels"]
    attempts = state.get("planning_attempts", 0)
    if not flights:
        warnings.append(f"No mock flight options are available for {state['origin']} to {state['destination']}.")
    if not hotels:
        warnings.append(f"No mock hotel options are available for {state['destination']}.")
    selected_flight = (
        min(flights, key=lambda item: item["price"])
        if attempts > 0 and flights
        else (flights[0] if flights else None)
    )
    selected_hotel = (
        min(hotels, key=lambda item: item["price_per_night"])
        if attempts > 0 and hotels
        else (max(hotels, key=lambda item: item["rating"]) if hotels else None)
    )
    nights = state["duration"]
    flight_cost = float(selected_flight["price"] * 2 * state["travelers"]) if selected_flight else 0.0
    hotel_cost = float(selected_hotel["price_per_night"] * nights * state["travelers"]) if selected_hotel else 0.0
    food_inr = float(1400 * nights * state["travelers"])
    transport_inr = float(600 * nights * state["travelers"])
    activity_daily = [1200, 700, 350][min(attempts, 2)]
    activity_inr = float(activity_daily * nights * state["travelers"])

    try:
        converted = await asyncio.gather(*[
            _in_user_currency(amount, state["currency"])
            for amount in (flight_cost, hotel_cost, food_inr, transport_inr, activity_inr)
        ])
        flight_user, hotel_user, food_user, transport_user, activity_user = converted
    except Exception as exc:
        errors.append(str(exc))
        warnings.append("One or more cost estimates could not be converted; displayed totals may be incomplete.")
        flight_user = hotel_user = food_user = transport_user = activity_user = 0.0

    total = round(flight_user + hotel_user + food_user + transport_user + activity_user, 2)
    return {
        "flights": flights,
        "hotels": hotels,
        "flight_cost": round(flight_user, 2),
        "hotel_cost": round(hotel_user, 2),
        "food_cost": round(food_user, 2),
        "transport_cost": round(transport_user, 2),
        "activity_cost": round(activity_user, 2),
        "total_cost": total,
        "remaining_budget": round(state["budget"] - total, 2),
        "budget_met": total <= state["budget"],
        "warnings": warnings,
        "errors": errors,
        "budget_checked": True,
        "selected_flight": selected_flight,
        "selected_hotel": selected_hotel,
        "currency_conversion_source": "Frankfurter API; mock catalogue prices are supplied in INR",
    }
