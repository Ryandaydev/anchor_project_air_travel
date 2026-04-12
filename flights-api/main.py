from datetime import date

from fastapi import Depends, FastAPI, Query
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from database import get_db
from schemas import Flight

app = FastAPI()


@app.get(
    "/",
    summary="Check to see if the Flights API is running",
    description="""Use this endpoint to check if the API is running. You can also check it first before making other calls to be sure it's running.""",
    response_description="A JSON record with a message in it. If the API is running the message will say successful.",
    operation_id="v0_health_check",
    tags=["analytics"],
)
async def root():
    return {"message": "API health check successful"}

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