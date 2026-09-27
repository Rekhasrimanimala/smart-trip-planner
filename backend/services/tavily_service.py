import asyncio
from datetime import date
from typing import Any

from tavily import TavilyClient

from backend.config import get_settings

CATEGORIES = {
    "events": "local events",
    "festivals": "festivals",
    "closures": "attraction and transport closures",
    "advisories": "official travel advisories and safety alerts",
}


async def search_current_info(destination: str, start_date: date, end_date: date) -> dict[str, Any]:
    settings = get_settings()
    result = {key: [] for key in CATEGORIES}
    errors: list[str] = []
    if not settings.tavily_api_key:
        return {**result, "errors": ["Tavily is not configured; current events and advisories were not retrieved."]}

    client = TavilyClient(api_key=settings.tavily_api_key)
    date_range = f"{start_date.isoformat()} to {end_date.isoformat()}"

    def search(query: str) -> list[str]:
        response = client.search(query=query, search_depth="basic", max_results=4, topic="general")
        return [
            f"{item.get('title', 'Search result')}: {item.get('content', '').strip()} (source: {item.get('url', '')})"
            for item in response.get("results", [])
            if item.get("content")
        ]

    for key, topic in CATEGORIES.items():
        try:
            result[key] = await asyncio.to_thread(
                search, f"{topic} in {destination} during {date_range}; current information"
            )
        except Exception as exc:  # Provider failures must not stop trip planning.
            errors.append(f"Tavily {topic} search failed: {exc}")
    return {**result, "errors": errors}
