# Air Travel SDK

Python SDK for the Air Travel API.

## Installation

```bash
pip install air-travel
```

For local development:

```bash
uv pip install -e .
```

## Quick Start

```python
from air_travel import AirTravelClient

client = AirTravelClient()

health = client.health()
print(health)

flights = client.flights(
    carrier="AA",
    flightnumber="100",
    flight_date="2025-01-01",
)

for flight in flights:
    print(flight)
```

## Configuration

By default, the SDK uses:

```text
https://air-travel.fastapicloud.dev
```

To use a different environment:

```python
from air_travel import AirTravelClient

client = AirTravelClient(
    base_url="http://localhost:8000"
)
```

## API

### Health Check

```python
client.health()
```

### Search Flights

```python
client.flights(
    carrier="AA",
    flightnumber="100",
    flight_date="2025-01-01",
    skip=0,
    limit=100,
)
```

Parameters:

| Parameter | Type | Required |
|------------|--------|----------|
| carrier | str | No |
| flightnumber | str | No |
| flight_date | str (YYYY-MM-DD) | No |
| skip | int | No |
| limit | int | No |

## License

MIT