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
async def test_airlines_local_api():
    async with AsyncAirTravelClient(
        base_url="http://127.0.0.1:8000"
    ) as client:
        airlines = await client.airlines()

    assert isinstance(airlines, list)
    assert len(airlines) > 0

    assert airlines[0]["carrier"] == "AA"
    assert airlines[0]["carrier_name"] == "American Airlines"