import re
from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.api.schemas import AskRequest, TripRequest
from backend.graph.trip_graph import run_trip
from backend.rag.retriever import retrieve
from backend.services.llm_service import invoke_json
from backend.services.weather_service import get_weather

router = APIRouter(prefix="/api")


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/plan-trip")
async def plan_trip(request: TripRequest) -> dict[str, Any]:
    try:
        return await run_trip(request.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Trip planning failed: {exc}") from exc


@router.post("/ask")
async def ask(request: AskRequest) -> dict[str, Any]:
    question = request.question
    destination = request.destination
    if not destination:
        match = re.search(r"(?:visit|in|to)\s+([A-Z][a-zA-Z-]+(?:\s+[A-Z][a-zA-Z-]+)?)", question)
        destination = match.group(1) if match else None
    lowered = question.casefold()
    if any(word in lowered for word in ("visa", "passport", "entry requirement")):
        if not destination:
            return {"answer": "Please name the destination country for visa guidance.", "sources": []}
        country_match = re.search(r"\b([A-Z][a-zA-Z-]+)\s+passport\b", question)
        passport = country_match.group(1) if country_match else request.passport_country
        try:
            documents = retrieve(f"visa policy {destination} traveler passport {passport}", limit=4)
            context = "\n".join(item["text"] for item in documents)
            generated = invoke_json(
                "Answer only using the retrieved travel knowledge. Do not invent a visa decision. Output JSON with answer.",
                f"Question: {question}\nRetrieved knowledge:\n{context}",
            )
            answer = generated.get("answer") if generated else context
            return {
                "answer": answer or "No relevant visa guidance was found in the local knowledge base.",
                "sources": sorted({item["source"] for item in documents}),
                "warning": "Visa requirements can change. Please verify the latest requirements with the relevant official embassy or immigration website before travelling.",
            }
        except Exception as exc:
            return {"answer": "Visa guidance is currently unavailable because the knowledge base could not be queried.", "sources": [], "error": str(exc)}
    if "weather" in lowered or "forecast" in lowered:
        if not destination:
            return {"answer": "Please provide a destination for the weather forecast."}
        start = request.start_date or date.today() + timedelta(days=1)
        end = request.end_date or start + timedelta(days=6)
        weather = await get_weather(destination, start, end)
        return {"destination": destination, "weather": weather}
    return {"answer": "Use the trip planner for a full itinerary, budget, current events and advisory search. For a quick answer, ask about visa requirements or destination weather."}