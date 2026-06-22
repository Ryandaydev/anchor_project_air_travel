"""
FastMCP Air Travel Server
"""

import logging
from typing import Optional

from fastmcp import FastMCP

from air_travel import (
    AirTravelAPIError,
    AirTravelClient,
    AirTravelRequestError,
)

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

mcp = FastMCP("Air Travel Server")

client = AirTravelClient()


@mcp.tool
async def get_flights(
    carrier: Optional[str] = None,
    flightnumber: Optional[str] = None,
    flight_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> str:
    """Search for flights based on carrier, flight number, and flight date."""
    try:
        data = client.flights(
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
            f"Departure Delay: {flight.get('dep_delay_minutes', 'N/A')} minutes\n"
            f"Arrival Delay: {flight.get('arr_delay_minutes', 'N/A')} minutes\n"
            f"Cancelled: {flight.get('cancelled', 'N/A')}\n"
            f"Diverted: {flight.get('diverted', 'N/A')}\n"
            f"Operating Airline: {flight.get('operating_airline', 'N/A')}\n"
            f"Tail Number: {flight.get('tail_number', 'N/A')}\n"
            "---"
        )

    return "\n".join(flights)


@mcp.tool
async def health_check() -> str:
    """Check if the Air Travel API is running."""
    try:
        response = client.health()
        return f"API is healthy\n{response}"
    except AirTravelAPIError as e:
        return str(e)
    except AirTravelRequestError as e:
        return str(e)


@mcp.tool
async def get_airline_codes(
    code: Optional[str] = None,
) -> dict[str, str] | str:
    """
    Return DOT/BTS airline carrier codes mapped to airline names.

    If code is provided, return only that airline.
    """
    airline_codes = {
        "AA": "American Airlines Inc.",
        "AS": "Alaska Airlines Inc.",
        "B6": "JetBlue Airways",
        "DL": "Delta Air Lines Inc.",
        "F9": "Frontier Airlines Inc.",
        "G4": "Allegiant Air",
        "HA": "Hawaiian Airlines Inc.",
        "NK": "Spirit Air Lines",
        "SY": "Sun Country Airlines d/b/a MN Airlines",
        "UA": "United Air Lines Inc.",
        "WN": "Southwest Airlines Co.",
    }

    if code:
        normalized_code = code.upper()
        airline = airline_codes.get(normalized_code)

        if not airline:
            return f"No airline found for code: {normalized_code}"

        return f"{normalized_code}: {airline}"

    return airline_codes


if __name__ == "__main__":
    mcp.run()