# Smart Trip Planner

## Project Objective

Waypoint creates a date-aware, budget-checked travel plan from an origin, destination, travel dates, budget and traveller details. It combines local mock booking catalogues with retrieved travel knowledge and live weather/current-information providers.

## Features

- Day-by-day itinerary with weather-aware indoor alternatives.
- Mock flight and hotel options, explicit return-fare cost estimate, and user-currency cost breakdown.
- Bounded budget re-planning (three retries after the initial plan).
- ChromaDB RAG for destination guidance, visa references and travel insurance basics, with source citations.
- Date-scoped Tavily searches for events, festivals, closures and travel advisories.
- Open-Meteo geocoding and forecast lookups.
- Quick `/api/ask` queries for visa and destination-weather questions.

## Architecture

The FastAPI API validates request inputs and invokes a LangGraph `StateGraph`. The planner writes the execution tasks and budget strategy. Executors retrieve destination/visa context, current information, weather, itinerary and costs. A conditional edge returns an over-budget result to the planner; after three re-plans the closest estimate is returned with an explicit warning. An optional OpenAI chat model is used for grounded itinerary/visa wording when `OPENAI_API_KEY` is configured; deterministic, retrieval-grounded behavior remains available without it.

### Agent Architecture

`START → Planner → Itinerary Agent → Weather Agent → Budget Agent → Budget Check`

Budget Check returns to Planner while the estimate exceeds the budget and fewer than three re-planning attempts have been made. Otherwise it calls Booking Summary Agent and ends. Each itinerary has one entry for each calendar day from start date up to, but not including, end date.

### MCP Tools

The Python MCP server exposes `search_flights`, `search_hotels` and `convert_currency`. Flight and hotel data are loaded from JSON files and are not connected to booking systems. Currency conversion calls the Frankfurter API and reports provider failures instead of substituting a hard-coded exchange rate.

### RAG

Markdown source documents live under `backend/rag/documents/`. The ingestion command splits them into overlapping chunks and stores text embeddings in a persistent ChromaDB collection. Retrieval returns source filenames alongside each chunk; visa answers cite those filenames. The Chroma default embedding function may download its local embedding model on first use.

### Tavily

When `TAVILY_API_KEY` is available, four separate date-scoped searches cover local events, festivals, closures and travel advisories. Missing keys and provider errors appear as warnings; the application does not invent current-event results.

### Open-Meteo

The weather adapter geocodes the destination and requests daily temperature, precipitation probability and weather codes for the available forecast window. Open-Meteo forecast availability is limited; trips beyond its range are labeled rather than given invented forecasts.

### Frankfurter

Frankfurter supplies exchange rates for budget conversions. The budget's mock catalogue values are in INR; conversion errors are surfaced and affected estimates are labeled incomplete.

## Technologies

Python 3.11+, FastAPI, Pydantic, LangGraph, MCP Python SDK, ChromaDB, Tavily, Open-Meteo, Frankfurter, React 18 and Vite.

## Folder Structure

```text
backend/
  agents/       Planner, itinerary, weather, budget and summary nodes
  api/          FastAPI routes and request models
  data/         Mock flight and hotel JSON
  graph/        Shared state and conditional LangGraph workflow
  mcp/          MCP server and three tools
  rag/          Chroma ingestion, retrieval and source documents
  services/     Tavily, weather and optional LLM adapters
frontend/       React + Vite application
tests/          API, integration, budget and MCP tests
```

## Installation

From the project root, create and activate a virtual environment, then install Python dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add provider keys as available. Never commit `.env`.

## Environment Variables

- `TAVILY_API_KEY`: required for current event, festival, closure and advisory search.
- `OPENAI_API_KEY`: optional; enables LLM-generated wording grounded in supplied RAG/search/weather context.
- `OPENAI_MODEL`: optional model name (defaults to `gpt-4o-mini`).
- `CHROMA_PATH`: optional persistent vector-store path.

The application remains available without Tavily/OpenAI keys, with current-search and LLM-dependent capabilities labeled or using deterministic retrieved context.

## RAG Setup

After Python dependencies are installed, index the included documents:

```powershell
python -m backend.rag.ingest
```

The API also attempts ingestion on first retrieval if the collection is empty.

## MCP Setup

Run the stdio MCP server from the project root:

```powershell
python -m backend.mcp.server
```

Configure an MCP client to launch that command with the project root as its working directory. The server registers the same tool functions used by the Budget Agent.

## Backend Startup

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/api/health`.

Plan endpoint: `POST http://localhost:8000/api/plan-trip`.

Quick visa/weather question endpoint: `POST http://localhost:8000/api/ask` with a `question` and optional destination/passport/date fields.

## Frontend Startup

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL (normally `http://localhost:5173`). Its development proxy forwards `/api` requests to FastAPI at port 8000.

## Example Queries

The form supports trips such as Chennai to Singapore, 10–14 December 2026, budget INR 80,000. It requires origin, destination, dates and a positive budget. The quick endpoint supports questions such as “Do I need a visa to visit Thailand on an Indian passport?” and “What's the weather like in Munnar next week?”.

## Expected Output

The trip response contains trip summary, mock flight/hotel options, weather, source-cited visa context, date-relevant events/festivals/closures/advisories, one itinerary entry per trip day, line-item costs, remaining budget, re-planning count and warnings.

## Tests

```powershell
pytest -q
```

Tests mock external services and exercise tools, input validation, the conditional retry loop, quick visa/weather queries and a complete sample trip without needing provider keys.

## Limitations

- Flights and hotels are MOCK data. The application does not book flights or hotels.
- Prices are indicative and may change; the sample one-way flight fare is doubled for the return-trip budget estimate.
- Visa information is general knowledge-base guidance and must always be verified against official government/embassy sources.
- Current events and advisories depend on available Tavily search results and a configured API key.
- Forecasts are limited to the Open-Meteo forecast window; farther-out trip dates may have no forecast yet.
- Without `OPENAI_API_KEY`, itinerary and visa wording use deterministic logic and retrieved source text rather than LLM generation.

Flight and hotel prices are indicative and may change. Please verify prices before booking.

Visa requirements can change. Please verify the latest requirements with the relevant official embassy or immigration website before travelling.