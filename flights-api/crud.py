from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Flight


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

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())