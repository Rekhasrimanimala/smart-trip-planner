import json
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "hotels.json"


def search_hotels(city: str, check_in: str, check_out: str) -> dict[str, Any]:
    """Return matching mock hotels; no live booking provider is contacted."""
    rows = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    hotels = [
        {key: row[key] for key in ("name", "price_per_night", "currency", "rating")}
        for row in rows
        if row["city"].casefold() == city.strip().casefold()
    ]
    return {"city": city, "check_in": check_in, "check_out": check_out, "hotels": hotels}
