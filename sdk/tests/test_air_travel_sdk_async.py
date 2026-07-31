import pytest

from air_travel import AsyncAirTravelClient


@pytest.mark.asyncio
async def test_health_check_returns_dict():
    """Tests health check from asynchronous SDK."""
    async with AsyncAirTravelClient() as client:
        response = await client.health()

    assert isinstance(response, dict)


@pytest.mark.asyncio
async def test_flights_returns_list():
    """Tests searching flights from asynchronous SDK."""
    async with AsyncAirTravelClient() as client:
        flights = await client.flights(limit=10)

    assert isinstance(flights, list)


@pytest.mark.asyncio
async def test_flights_with_carrier_filter_returns_list():
    """Tests searching flights with a carrier filter."""
    async with AsyncAirTravelClient() as client:
        flights = await client.flights(
            carrier="AA",
            limit=10,
        )

    assert isinstance(flights, list)


@pytest.mark.asyncio
async def test_flight_records_have_expected_fields():
    """Tests flight records include expected API fields."""
    async with AsyncAirTravelClient() as client:
        flights = await client.flights(limit=1)

    if not flights:
        pytest.skip("No flights returned from API.")

    flight = flights[0]

    expected_fields = {
        "id",
        "flight_date",
        "iata_code_marketing_airline",
        "flight_number_marketing_airline",
        "origin",
        "origin_city_name",
        "dest",
        "dest_city_name",
    }

    for field in expected_fields:
        assert field in flight


@pytest.mark.asyncio
async def test_carriers_returns_list():
    """Tests listing carriers from asynchronous SDK."""
    async with AsyncAirTravelClient() as client:
        carriers = await client.carriers()

    assert isinstance(carriers, list)
    assert {"code": "UA", "name": "United Air Lines Inc."} in carriers


@pytest.mark.asyncio
async def test_carriers_with_code_filter_returns_single_carrier():
    """Tests looking up a single carrier by code."""
    async with AsyncAirTravelClient() as client:
        carriers = await client.carriers(code="ua")

    assert carriers == [{"code": "UA", "name": "United Air Lines Inc."}]