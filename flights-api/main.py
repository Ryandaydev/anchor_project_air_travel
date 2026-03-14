from datetime import date

from fastapi import Depends, FastAPI, Query
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from database import get_db
from schemas import Flight

app = FastAPI()


@app.get("/v0/flights", response_model=list[Flight])
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