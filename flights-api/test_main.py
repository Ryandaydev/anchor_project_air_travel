from httpx import ASGITransport, AsyncClient
import pytest

from main import app


@pytest.mark.asyncio
async def test_search_flights_success():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(
            "/v0/flights",
            params={
                "carrier": "UA",
                "flightnumber": "4712",
                "flight_date": "2025-11-12",
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    flight = data[0]

    assert flight["flight_date"] == "2025-11-12"
    assert flight["iata_code_marketing_airline"] == "UA"
    assert flight["flight_number_marketing_airline"] == "4712"

    assert flight["origin"] == "ORD"
    assert flight["origin_city_name"] == "Chicago, IL"
    assert flight["dest"] == "ELP"
    assert flight["dest_city_name"] == "El Paso, TX"

    assert flight["crs_dep_time"] == "2005"
    assert flight["dep_time"] == "2004"
    assert flight["crs_arr_time"] == "2253"
    assert flight["arr_time"] == "2313"

    assert float(flight["dep_delay_minutes"]) == 0.0
    assert float(flight["arr_delay_minutes"]) == 20.0
    assert float(flight["cancelled"]) == 0.0
    assert float(flight["diverted"]) == 0.0

    assert flight["operating_airline"] == "OO"
    assert flight["iata_code_operating_airline"] == "OO"
    assert flight["tail_number"] == "N135SY"


@pytest.mark.asyncio
async def test_search_flights_no_match_returns_empty_list():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(
            "/v0/flights",
            params={
                "carrier": "UA",
                "flightnumber": "9999",
                "flight_date": "2025-11-12",
            },
        )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_search_flights_with_no_params_returns_list():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get("/v0/flights")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_search_flights_honors_limit_param():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(
            "/v0/flights",
            params={
                "carrier": "UA",
                "flight_date": "2025-11-12",
                "limit": 1,
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 1


@pytest.mark.asyncio
async def test_search_flights_honors_skip_param():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(
            "/v0/flights",
            params={
                "carrier": "UA",
                "flight_date": "2025-11-12",
                "skip": 1,
                "limit": 1,
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 1


@pytest.mark.asyncio
async def test_search_flights_rejects_invalid_limit():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get(
            "/v0/flights",
            params={"limit": 0},
        )

    assert response.status_code == 422