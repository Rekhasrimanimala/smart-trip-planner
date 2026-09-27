from typing import Any, NotRequired, TypedDict


class TripState(TypedDict):
    user_request: str
    origin: str
    destination: str
    start_date: str
    end_date: str
    duration: int
    budget: float
    currency: str
    travelers: int
    preferences: str
    passport_country: str
    execution_plan: list[str]
    planning_attempts: int
    flights: list[dict[str, Any]]
    hotels: list[dict[str, Any]]
    visa_info: str
    visa_sources: list[str]
    events: list[str]
    festivals: list[str]
    closures: list[str]
    advisories: list[str]
    weather: list[dict[str, Any]]
    itinerary: list[dict[str, Any]]
    food_cost: float
    transport_cost: float
    activity_cost: float
    flight_cost: float
    hotel_cost: float
    total_cost: float
    remaining_budget: float
    budget_met: bool
    warnings: list[str]
    errors: list[str]
    budget_checked: NotRequired[bool]
    weather_summary: NotRequired[dict[str, Any]]
    selected_flight: NotRequired[dict[str, Any] | None]
    selected_hotel: NotRequired[dict[str, Any] | None]
    currency_conversion_source: NotRequired[str]
    summary: NotRequired[dict[str, Any]]
