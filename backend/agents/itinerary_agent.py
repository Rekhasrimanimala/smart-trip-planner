from datetime import date, timedelta
from typing import Any

from backend.graph.state import TripState
from backend.rag.retriever import retrieve
from backend.services.llm_service import invoke_json
from backend.services.tavily_service import search_current_info
from backend.services.weather_service import get_weather


def _weather_rainy(weather_day: dict[str, Any]) -> bool:
    code = weather_day.get("weather_code")
    rain_chance = weather_day.get("precipitation_probability") or 0
    return (isinstance(code, (int, float)) and code >= 51) or rain_chance >= 55


async def itinerary_agent(state: TripState) -> dict[str, Any]:
    errors = list(state.get("errors", []))
    warnings = list(state.get("warnings", []))
    context: list[dict[str, str]] = []
    visa_info = "Visa information could not be retrieved from the local knowledge base."
    visa_sources: list[str] = []
    try:
        context = retrieve(f"{state['destination']} destination guide travel visa policy attractions {state['preferences']}", limit=6)
        visa_context = retrieve(
            f"Visa requirements for a traveler holding a {state['passport_country']} passport visiting {state['destination']}",
            limit=4,
        )
        visa_sources = sorted({item["source"] for item in visa_context})
        visa_info = " ".join(item["text"] for item in visa_context)
    except Exception as exc:
        errors.append(f"RAG retrieval failed: {exc}")
        warnings.append("Visa guidance is unavailable because the local knowledge base could not be queried.")

    try:
        current = await search_current_info(
            state["destination"], date.fromisoformat(state["start_date"]), date.fromisoformat(state["end_date"])
        )
    except Exception as exc:
        current = {"events": [], "festivals": [], "closures": [], "advisories": [], "errors": [str(exc)]}
    warnings.extend(current.get("errors", []))

    guide = "\n".join(item["text"] for item in context)
    weather_summary = await get_weather(
        state["destination"], date.fromisoformat(state["start_date"]), date.fromisoformat(state["end_date"])
    )
    weather = weather_summary.get("days", [])
    if weather_summary.get("error"):
        warnings.append(weather_summary["error"])
    system_prompt = (
        "Create a practical travel itinerary as JSON with a days array. Each day must have date, morning, "
        "afternoon, evening. Use only supplied guide and web context for factual event/closure claims. "
        "Never schedule an activity explicitly reported closed. Prefer indoor plans on rainy days."
    )
    user_prompt = (
        f"Destination: {state['destination']}; dates: {state['start_date']} through {state['end_date']}; "
        f"preferences: {state['preferences']}; weather: {weather}; guide: {guide}; "
        f"events: {current.get('events', [])}; festivals: {current.get('festivals', [])}; "
        f"closures: {current.get('closures', [])}; advisories: {current.get('advisories', [])}. "
        f"Return exactly {state['duration']} day entries."
    )
    generated = invoke_json(system_prompt, user_prompt)
    itinerary = generated.get("days", []) if generated else []
    expected_dates = [
        (date.fromisoformat(state["start_date"]) + timedelta(days=index)).isoformat()
        for index in range(state["duration"])
    ]
    valid_llm_days = len(itinerary) == state["duration"] and all(
        isinstance(day, dict) and all(day.get(slot) for slot in ("morning", "afternoon", "evening"))
        for day in itinerary
    )
    if not valid_llm_days:
        indoor = ["National museum or gallery", "Covered market and local food hall", "Indoor gardens or conservatory"]
        outdoor = ["Historic district and landmark walk", "Botanic garden or waterfront", "Local neighborhood and viewpoint"]
        itinerary = []
        for index, day_date in enumerate(expected_dates):
            weather_day = next((item for item in weather if item.get("date") == day_date), {})
            activities = indoor if _weather_rainy(weather_day) else outdoor
            itinerary.append({
                "date": day_date,
                "morning": activities[index % len(activities)],
                "afternoon": activities[(index + 1) % len(activities)],
                "evening": "Dinner near the accommodation; check local operating hours",
            })
    else:
        for day, day_date in zip(itinerary, expected_dates):
            day["date"] = day_date

    closure_text = " ".join(current.get("closures", [])).casefold()
    if closure_text:
        for day in itinerary:
            for slot in ("morning", "afternoon", "evening"):
                activity = str(day.get(slot, ""))
                if activity.casefold() in closure_text:
                    day[slot] = "Choose an open nearby attraction; verify local operating notices"
    visa_answer = invoke_json(
        "Answer the visa question only from the supplied retrieved knowledge. State uncertainty and advise official verification.",
        f"Question: Does a {state['passport_country']} passport holder need a visa for {state['destination']}? Retrieved knowledge: {visa_info}",
    )
    if visa_answer and visa_answer.get("answer"):
        visa_info = str(visa_answer["answer"])
    return {
        "itinerary": itinerary,
        "weather": weather,
        "weather_summary": weather_summary,
        "visa_info": visa_info,
        "visa_sources": visa_sources,
        "events": current.get("events", []),
        "festivals": current.get("festivals", []),
        "closures": current.get("closures", []),
        "advisories": current.get("advisories", []),
        "warnings": warnings,
        "errors": errors,
        "_guide_context": guide,
    }
