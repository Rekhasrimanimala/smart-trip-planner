from mcp.server.fastmcp import FastMCP

from backend.mcp.currency_tools import convert_currency
from backend.mcp.flight_tools import search_flights
from backend.mcp.hotel_tools import search_hotels

mcp = FastMCP("smart-trip-planner")

mcp.tool()(search_flights)
mcp.tool()(search_hotels)
mcp.tool()(convert_currency)


if __name__ == "__main__":
    mcp.run()
