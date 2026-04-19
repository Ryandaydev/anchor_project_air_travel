"""
FastMCP Air Travel Server (FastMCP 3.x)
"""

import logging
from typing import Any, Optional

import httpx
from fastmcp import FastMCP

# Logging setup
logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Create server
mcp = FastMCP("Air Travel Server")

AIR_TRAVEL_API_BASE = "https://air-travel.fastapicloud.dev"


async def make_air_travel_request(url: str, params: Optional[dict] = None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            return f"HTTP ERROR {e.response.status_code}: {e.response.text}"

        except Exception as e:
            return f"REQUEST FAILED: {type(e).__name__}: {str(e)}"


@mcp.tool
async def get_flights(
    carrier: Optional[str] = None,
    flightnumber: Optional[str] = None,
    flight_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> str:
    """Search for flights based on carrier, flight number, and flight date. Returns a list of matching flights."""
    params = {}
    if carrier:
        params['carrier'] = carrier
    if flightnumber:
        params['flightnumber'] = flightnumber
    if flight_date:
        params['flight_date'] = flight_date
    params['skip'] = skip
    params['limit'] = limit

    url = f"{AIR_TRAVEL_API_BASE}/v0/flights"
    data = await make_air_travel_request(url, params)

    if not data:
        return "Unable to fetch flights."

    # Format the response
    flights = []
    for flight in data:
        flight_info = (
            f"Flight ID: {flight.get('id', 'N/A')}\n"
            f"Date: {flight.get('flight_date', 'N/A')}\n"
            f"Carrier: {flight.get('iata_code_marketing_airline', 'N/A')} {flight.get('flight_number_marketing_airline', 'N/A')}\n"
            f"Route: {flight.get('origin', 'N/A')} ({flight.get('origin_city_name', 'N/A')}) to {flight.get('dest', 'N/A')} ({flight.get('dest_city_name', 'N/A')})\n"
            f"Scheduled Departure: {flight.get('crs_dep_time', 'N/A')}\n"
            f"Actual Departure: {flight.get('dep_time', 'N/A')}\n"
            f"Scheduled Arrival: {flight.get('crs_arr_time', 'N/A')}\n"
            f"Actual Arrival: {flight.get('arr_time', 'N/A')}\n"
            f"Departure Delay: {flight.get('dep_delay_minutes', 'N/A')} minutes\n"
            f"Arrival Delay: {flight.get('arr_delay_minutes', 'N/A')} minutes\n"
            f"Cancelled: {flight.get('cancelled', 'N/A')}\n"
            f"Diverted: {flight.get('diverted', 'N/A')}\n"
            f"Operating Airline: {flight.get('operating_airline', 'N/A')}\n"
            f"Tail Number: {flight.get('tail_number', 'N/A')}\n"
            "---"
        )
        flights.append(flight_info)
    
    return "\n".join(flights) if flights else "No flights found."


@mcp.tool
async def health_check() -> str:
    """Check if the Air Travel API is running."""
    url = f"{AIR_TRAVEL_API_BASE}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()

            data = response.json()
            return f"Health check success: {data.get('message', 'No message returned')}"

        except httpx.HTTPStatusError as e:
            return f"HTTP error {e.response.status_code}: {e.response.text}"

        except Exception as e:
            return f"Request failed: {type(e).__name__}: {str(e)}"

# Server entrypoint
if __name__ == "__main__":
    mcp.run()  