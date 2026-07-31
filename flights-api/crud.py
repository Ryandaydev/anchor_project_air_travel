from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Flight
from schemas import Carrier

# DOT/BTS airline carrier codes mapped to airline names.
CARRIER_CODES: dict[str, str] = {
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


async def search_flights(
    db: AsyncSession,
    carrier: str | None = None,
    flight_number: str | None = None,
    flight_date: date | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Flight]:
    stmt = select(Flight)

    if carrier:
        stmt = stmt.where(Flight.iata_code_marketing_airline == carrier)

    if flight_number:
        stmt = stmt.where(Flight.flight_number_marketing_airline == flight_number)

    if flight_date:
        stmt = stmt.where(Flight.flight_date == flight_date)

    stmt = stmt.order_by(Flight.id)
    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())


def search_carriers(code: str | None = None) -> list[Carrier]:
    if code:
        normalized_code = code.upper()
        name = CARRIER_CODES.get(normalized_code)

        if not name:
            return []

        return [Carrier(code=normalized_code, name=name)]

    return [
        Carrier(code=code, name=name) for code, name in CARRIER_CODES.items()
    ]