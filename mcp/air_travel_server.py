
"""
FastMCP Air Travel Server
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastmcp import FastMCP

from air_travel import (
    AirTravelAPIError,
    AirTravelRequestError,
    AsyncAirTravelClient,
)

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


client: AsyncAirTravelClient | None = None


@asynccontextmanager
async def app_lifespan(
    server: FastMCP,
) -> AsyncIterator[dict]:
    """Create and close the shared asynchronous API client."""
    global client

    client = AsyncAirTravelClient()

    try:
        yield {}
    finally:
        await client.aclose()
        client = None


mcp = FastMCP(
    "Air Travel Server",
    lifespan=app_lifespan,
)


def get_client() -> AsyncAirTravelClient:
    """Return the initialized asynchronous API client."""
    if client is None:
        raise RuntimeError("The Air Travel API client is not initialized.")

    return client


@mcp.tool
async def get_flights(
    carrier: str | None = None,
    flightnumber: str | None = None,
    flight_date: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> str:
    """Search for flights based on carrier, flight number, and flight date."""
    try:
        data = await get_client().flights(
            carrier=carrier,
            flightnumber=flightnumber,
            flight_date=flight_date,
            skip=skip,
            limit=limit,
        )
    except AirTravelAPIError as e:
        return str(e)
    except AirTravelRequestError as e:
        return str(e)

    if not data:
        return "No flights found."

    flights = []

    for flight in data:
        flights.append(
            f"Flight ID: {flight.get('id', 'N/A')}\n"
            f"Date: {flight.get('flight_date', 'N/A')}\n"
            f"Carrier: {flight.get('iata_code_marketing_airline', 'N/A')} "
            f"{flight.get('flight_number_marketing_airline', 'N/A')}\n"
            f"Route: {flight.get('origin', 'N/A')} "
            f"({flight.get('origin_city_name', 'N/A')}) "
            f"to {flight.get('dest', 'N/A')} "
            f"({flight.get('dest_city_name', 'N/A')})\n"
            f"Scheduled Departure: {flight.get('crs_dep_time', 'N/A')}\n"
            f"Actual Departure: {flight.get('dep_time', 'N/A')}\n"
            f"Scheduled Arrival: {flight.get('crs_arr_time', 'N/A')}\n"
            f"Actual Arrival: {flight.get('arr_time', 'N/A')}\n"
            f"Departure Delay: "
            f"{flight.get('dep_delay_minutes', 'N/A')} minutes\n"
            f"Arrival Delay: "
            f"{flight.get('arr_delay_minutes', 'N/A')} minutes\n"
            f"Cancelled: {flight.get('cancelled', 'N/A')}\n"
            f"Diverted: {flight.get('diverted', 'N/A')}\n"
            f"Operating Airline: "
            f"{flight.get('operating_airline', 'N/A')}\n"
            f"Tail Number: {flight.get('tail_number', 'N/A')}\n"
            "---"
        )

    return "\n".join(flights)


@mcp.tool
async def health_check() -> str:
    """Check if the Air Travel API is running."""
    try:
        response = await get_client().health()
        return f"API is healthy\n{response}"
    except AirTravelAPIError as e:
        return str(e)
    except AirTravelRequestError as e:
        return str(e)


@mcp.tool
async def get_airline_codes(
    code: str | None = None,
) -> dict[str, str] | str:
    """
    Return DOT/BTS airline carrier codes mapped to airline names.

    If code is provided, return only that airline.
    """
    try:
        data = await get_client().carriers(code=code)
    except AirTravelAPIError as e:
        return str(e)
    except AirTravelRequestError as e:
        return str(e)

    if not data:
        if code:
            return f"No airline found for code: {code.upper()}"
        return "No carriers found."

    if code:
        carrier = data[0]
        return f"{carrier['code']}: {carrier['name']}"

    return {carrier["code"]: carrier["name"] for carrier in data}


if __name__ == "__main__":
    mcp.run()
