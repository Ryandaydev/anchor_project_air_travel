"""Testing SQLAlchemy helper functions for the flights API."""

from datetime import date

import pytest
import pytest_asyncio

import crud
from database import AsyncSessionLocal

SAMPLE_FLIGHT_DATE = date(2025, 11, 12)
SAMPLE_CARRIER = "UA"
SAMPLE_FLIGHT_NUMBER = "4712"


@pytest_asyncio.fixture
async def db_session():
    """Start an async database session and close it when done."""
    async with AsyncSessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_get_flight_by_carrier_flight_number_and_date(db_session):
    flight = await crud.get_flight_by_carrier_flight_number_and_date(
        db=db_session,
        carrier=SAMPLE_CARRIER,
        flight_number=SAMPLE_FLIGHT_NUMBER,
        flight_date=SAMPLE_FLIGHT_DATE,
    )

    assert flight is not None

    # identity
    assert flight.flight_date == SAMPLE_FLIGHT_DATE
    assert flight.iata_code_marketing_airline == "UA"
    assert flight.flight_number_marketing_airline == "4712"

    # route
    assert flight.origin == "ORD"
    assert flight.origin_city_name == "Chicago, IL"
    assert flight.dest == "ELP"
    assert flight.dest_city_name == "El Paso, TX"

    # scheduled times
    assert flight.crs_dep_time == "2005"
    assert flight.crs_arr_time == "2253"

    # actual operation
    assert flight.dep_time == "2004"
    assert flight.arr_time == "2313"

    # traveler-interest status fields
    assert float(flight.dep_delay_minutes) == 0.0
    assert float(flight.arr_delay_minutes) == 20.0
    assert float(flight.cancelled) == 0.0
    assert float(flight.diverted) == 0.0

    # operating-carrier detail
    assert flight.operating_airline == "OO"
    assert flight.iata_code_operating_airline == "OO"
    assert flight.tail_number == "N135SY"


@pytest.mark.asyncio
async def test_get_flight_returns_none_for_missing_match(db_session):
    flight = await crud.get_flight_by_carrier_flight_number_and_date(
        db=db_session,
        carrier="UA",
        flight_number="9999",
        flight_date=SAMPLE_FLIGHT_DATE,
    )

    assert flight is None