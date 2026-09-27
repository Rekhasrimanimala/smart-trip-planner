from typing import Any

import httpx


async def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict[str, Any]:
    source = from_currency.upper()
    target = to_currency.upper()
    if source == target:
        return {"amount": amount, "from_currency": source, "to_currency": target, "converted_amount": amount, "rate": 1.0}
    url = "https://api.frankfurter.dev/v1/latest"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url, params={"from": source, "to": target})
            response.raise_for_status()
            payload = response.json()
        rate = payload.get("rates", {}).get(target)
        if rate is None:
            raise ValueError(f"Frankfurter returned no rate for {source} to {target}.")
        return {
            "amount": amount,
            "from_currency": source,
            "to_currency": target,
            "converted_amount": round(amount * float(rate), 2),
            "rate": float(rate),
        }
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        raise RuntimeError(f"Currency conversion unavailable: {exc}") from exc
