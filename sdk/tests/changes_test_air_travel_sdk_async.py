

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