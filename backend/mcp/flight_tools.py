import json
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "flights.json"


def search_flights(origin: str, destination: str, date: str) -> dict[str, Any]:
    """Return matching mock flights; no live booking provider is contacted."""
    rows = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    flights = [
        {key: row[key] for key in ("airline", "flight_number", "departure", "arrival", "price", "currency")}
        for row in rows
        if row["origin"].casefold() == origin.strip().casefold()
        and row["destination"].casefold() == destination.strip().casefold()
    ]
    return {"origin": origin, "destination": destination, "date": date, "flights": flights}
