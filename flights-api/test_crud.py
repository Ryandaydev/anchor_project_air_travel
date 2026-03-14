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
    async with AsyncSessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_search_flights_returns_sample_row(db_session):
    flights = await crud.search_flights(
        db=db_session,
        carrier=SAMPLE_CARRIER,
        flight_number=SAMPLE_FLIGHT_NUMBER,
        flight_date=SAMPLE_FLIGHT_DATE,
    )

    assert flights is not None
    assert len(flights) >= 1

    flight = flights[0]

    assert flight.flight_date == SAMPLE_FLIGHT_DATE
    assert flight.iata_code_marketing_airline == "UA"
    assert flight.flight_number_marketing_airline == "4712"

    assert flight.origin == "ORD"
    assert flight.origin_city_name == "Chicago, IL"
    assert flight.dest == "ELP"
    assert flight.dest_city_name == "El Paso, TX"

    assert flight.crs_dep_time == "2005"
    assert flight.dep_time == "2004"
    assert flight.crs_arr_time == "2253"
    assert flight.arr_time == "2313"

    assert float(flight.dep_delay_minutes) == 0.0
    assert float(flight.arr_delay_minutes) == 20.0
    assert float(flight.cancelled) == 0.0
    assert float(flight.diverted) == 0.0

    assert flight.operating_airline == "OO"
    assert flight.iata_code_operating_airline == "OO"
    assert flight.tail_number == "N135SY"


@pytest.mark.asyncio
async def test_search_flights_returns_empty_list_for_missing_match(db_session):
    flights = await crud.search_flights(
        db=db_session,
        carrier="UA",
        flight_number="9999",
        flight_date=SAMPLE_FLIGHT_DATE,
    )

    assert flights == []


@pytest.mark.asyncio
async def test_search_flights_honors_limit(db_session):
    flights = await crud.search_flights(
        db=db_session,
        carrier=SAMPLE_CARRIER,
        flight_date=SAMPLE_FLIGHT_DATE,
        skip=0,
        limit=1,
    )

    assert len(flights) <= 1


@pytest.mark.asyncio
async def test_search_flights_uses_stable_ordering_for_pagination(db_session):
    first_page = await crud.search_flights(
        db=db_session,
        carrier=SAMPLE_CARRIER,
        flight_date=SAMPLE_FLIGHT_DATE,
        skip=0,
        limit=2,
    )

    second_page = await crud.search_flights(
        db=db_session,
        carrier=SAMPLE_CARRIER,
        flight_date=SAMPLE_FLIGHT_DATE,
        skip=2,
        limit=2,
    )

    first_ids = [flight.id for flight in first_page]
    second_ids = [flight.id for flight in second_page]

    assert first_ids == sorted(first_ids)
    assert second_ids == sorted(second_ids)

    if first_ids and second_ids:
        assert first_ids[-1] < second_ids[0]
        assert set(first_ids).isdisjoint(second_ids)