from datetime import date, timedelta
from typing import Any

import httpx


async def get_weather(destination: str, start_date: date, end_date: date) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            geo = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": destination, "count": 1, "language": "en", "format": "json"},
            )
            geo.raise_for_status()
            locations = geo.json().get("results", [])
            if not locations:
                raise ValueError(f"No weather location found for {destination}.")
            location = locations[0]
            today = date.today()
            forecast_end = min(end_date, today + timedelta(days=15))
            forecast_start = max(start_date, today)
            if forecast_start > forecast_end:
                return {"location": location.get("name", destination), "days": [], "note": "Forecast is not available for dates outside the Open-Meteo forecast window."}
            forecast = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                    "timezone": location.get("timezone", "auto"),
                    "start_date": forecast_start.isoformat(),
                    "end_date": forecast_end.isoformat(),
                },
            )
            forecast.raise_for_status()
            daily = forecast.json().get("daily", {})
        days = []
        for index, day in enumerate(daily.get("time", [])):
            days.append({
                "date": day,
                "weather_code": daily.get("weather_code", [None])[index],
                "temperature_min_c": daily.get("temperature_2m_min", [None])[index],
                "temperature_max_c": daily.get("temperature_2m_max", [None])[index],
                "precipitation_probability": daily.get("precipitation_probability_max", [None])[index],
            })
        return {"location": location.get("name", destination), "days": days, "note": "Forecast supplied by Open-Meteo; longer-range conditions are uncertain."}
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
        return {"location": destination, "days": [], "error": f"Weather information unavailable: {exc}"}
