from datetime import date

from fastapi import Depends, FastAPI, Query
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from database import get_db
from schemas import Flight

api_description = """
The Air Travel API provides read-only access to historical U.S. flight data.

The API is designed for data science, analytics, API development practice, and
agent/tool-calling demonstrations. It allows users to search flight records by
carrier, flight number, and flight date.

## Analytics

Use the health check endpoint to confirm that the API is running before making
other requests.

## Flight Info

Search for flights using optional filters such as carrier, flight number, and
flight date. Use skip and limit parameters to paginate through larger result
sets.

The flight data comes from the U.S. Department of Transportation Bureau of
Transportation Statistics airline on-time performance data.
"""

app = FastAPI(
    title="Air Travel API",
    description=api_description,
    version="0.1",
)


@app.get(
    "/",
    summary="Check to see if the Flights API is running",
    description="""Use this endpoint to check if the API is running. You can also check it first before making other calls to be sure it's running.""",
    response_description="A JSON record with a message in it. If the API is running the message will say successful.",
    operation_id="v0_health_check",
    tags=["analytics"],
)
async def root():
    return {"message": "API health check is successful"}

@app.get(
        "/v0/flights", 
        description="""Search for flights based on carrier, flight number, and flight date. You can also paginate the results using the skip and limit parameters.""",
        operation_id="v0_search_flights",
        tags=["flight info"],
        response_model=list[Flight])
async def search_flights(
    carrier: str | None = Query(default=None),
    flightnumber: str | None = Query(default=None),
    flight_date: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    flights = await crud.search_flights(
        db=db,
        carrier=carrier,
        flight_number=flightnumber,
        flight_date=flight_date,
        skip=skip,
        limit=limit,
    )

    return flights