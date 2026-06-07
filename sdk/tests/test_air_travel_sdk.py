import pytest

from air_travel import AirTravelClient


def test_health_check_returns_dict():
    """Tests health check from SDK."""
    client = AirTravelClient()

    response = client.health()

    assert isinstance(response, dict)


def test_flights_returns_list():
    """Tests searching flights from SDK."""
    client = AirTravelClient()

    flights = client.flights(limit=10)

    assert isinstance(flights, list)


def test_flights_with_carrier_filter_returns_list():
    """Tests searching flights with a carrier filter."""
    client = AirTravelClient()

    flights = client.flights(
        carrier="AA",
        limit=10,
    )

    assert isinstance(flights, list)


def test_flight_records_have_expected_fields():
    """Tests flight records include expected API fields."""
    client = AirTravelClient()

    flights = client.flights(limit=1)

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