def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_missing_budget_is_rejected(client, sample_payload):
    sample_payload.pop("budget")
    response = client.post("/api/plan-trip", json=sample_payload)
    assert response.status_code == 422
    assert any(error["loc"][-1] == "budget" for error in response.json()["detail"])


def test_missing_dates_are_rejected(client, sample_payload):
    sample_payload.pop("start_date")
    sample_payload.pop("end_date")
    response = client.post("/api/plan-trip", json=sample_payload)
    assert response.status_code == 422
    missing = {error["loc"][-1] for error in response.json()["detail"]}
    assert {"start_date", "end_date"}.issubset(missing)


def test_missing_origin_is_rejected(client, sample_payload):
    sample_payload.pop("origin")
    response = client.post("/api/plan-trip", json=sample_payload)
    assert response.status_code == 422
    assert any(error["loc"][-1] == "origin" for error in response.json()["detail"])


def test_end_date_must_follow_start_date(client, sample_payload):
    sample_payload["end_date"] = sample_payload["start_date"]
    response = client.post("/api/plan-trip", json=sample_payload)
    assert response.status_code == 422


def test_plan_trip_integration_replans_and_returns_complete_summary(client, sample_payload, monkeypatch):
    import backend.agents.itinerary_agent as itinerary
    import backend.agents.budget_agent as budget

    monkeypatch.setattr(itinerary, "retrieve", lambda *args, **kwargs: [{"text": "Singapore city guide and ICA visa information.", "source": "singapore.md"}])

    async def current_info(*args, **kwargs):
        return {"events": [], "festivals": [], "closures": [], "advisories": [], "errors": []}

    async def weather(*args, **kwargs):
        return {"location": "Singapore", "days": [], "note": "Forecast unavailable beyond the forecast window."}

    async def conversion(amount, source, target):
        assert source == target == "INR"
        return {"converted_amount": amount}

    monkeypatch.setattr(itinerary, "search_current_info", current_info)
    monkeypatch.setattr(itinerary, "get_weather", weather)
    monkeypatch.setattr(budget, "convert_currency", conversion)
    response = client.post("/api/plan-trip", json=sample_payload)

    assert response.status_code == 200, response.text
    result = response.json()
    assert len(result["itinerary"]) == 4
    assert result["trip_summary"]["destination"] == "Singapore"
    assert result["visa"]["sources"] == ["singapore.md"]
    assert result["budget_breakdown"]["total"] > 0
    assert result["budget_breakdown"]["budget_met"] is True
    assert result["planning_attempts"] == 1
    assert any("Visa requirements can change" in warning for warning in result["warnings"])
    assert any("Flight and hotel prices are indicative" in warning for warning in result["warnings"])


def test_budget_still_over_after_max_replans(client, sample_payload, monkeypatch):
    import backend.agents.itinerary_agent as itinerary
    import backend.agents.budget_agent as budget

    sample_payload["budget"] = 1000
    monkeypatch.setattr(itinerary, "retrieve", lambda *args, **kwargs: [{"text": "Travel guide.", "source": "singapore.md"}])

    async def current_info(*args, **kwargs):
        return {"events": [], "festivals": [], "closures": [], "advisories": [], "errors": []}

    async def weather(*args, **kwargs):
        return {"location": "Singapore", "days": []}

    async def conversion(amount, source, target):
        return {"converted_amount": amount}

    monkeypatch.setattr(itinerary, "search_current_info", current_info)
    monkeypatch.setattr(itinerary, "get_weather", weather)
    monkeypatch.setattr(budget, "convert_currency", conversion)
    response = client.post("/api/plan-trip", json=sample_payload)
    result = response.json()
    assert response.status_code == 200
    assert result["planning_attempts"] == 3
    assert result["budget_breakdown"]["budget_met"] is False
    assert any("could not be met after 3 planning attempts" in warning for warning in result["warnings"])


def test_visa_question_returns_rag_citation(client, monkeypatch):
    import backend.api.routes as routes

    monkeypatch.setattr(routes, "retrieve", lambda *args, **kwargs: [{"text": "Check the Thai Ministry of Foreign Affairs for passport-specific rules.", "source": "thailand.md"}])
    response = client.post("/api/ask", json={"question": "Do I need a visa to visit Thailand on an Indian passport?"})
    assert response.status_code == 200
    assert response.json()["sources"] == ["thailand.md"]
    assert "Visa requirements can change" in response.json()["warning"]


def test_weather_question_accepts_destination(client, monkeypatch):
    import backend.api.routes as routes

    async def weather(destination, start_date, end_date):
        return {"location": destination, "days": [{"date": start_date.isoformat()}]}

    monkeypatch.setattr(routes, "get_weather", weather)
    response = client.post("/api/ask", json={"question": "What's the weather like in Munnar next week?"})
    assert response.status_code == 200
    assert response.json()["destination"] == "Munnar"
    assert response.json()["weather"]["days"]
