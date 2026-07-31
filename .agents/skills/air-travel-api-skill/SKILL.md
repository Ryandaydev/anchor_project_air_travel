# Air Travel API Skill

## Purpose
Use this skill when you need to check whether the Air Travel API is running or search for individual flight records by marketing carrier, flight number, and flight date.

Base API URL:

```text
https://air-travel.fastapicloud.dev
```

## Health Check

Use the health check endpoint before making other requests when you need to confirm that the API is available.

### Endpoint

```http
GET /
```

### Example request

```bash
curl https://air-travel.fastapicloud.dev/
```

### Expected response

```json
{
  "message": "API health check is successful"
}
```

### How to interpret it
If the request returns HTTP 200 and the success message, the API is running.

## Search Flights

Use this endpoint to search flight records. The most useful filters are carrier, flight number, and flight date.

### Endpoint

```http
GET /v0/flights
```

### Query parameters

| Parameter | Type | Required | Description |
|---|---:|---:|---|
| `carrier` | string | No | Marketing airline IATA carrier code, such as `AA`, `DL`, `UA`, or `WN`. |
| `flightnumber` | string | No | Marketing airline flight number. |
| `flight_date` | date string | No | Flight date in `YYYY-MM-DD` format. |
| `skip` | integer | No | Number of records to skip for pagination. Default is `0`. |
| `limit` | integer | No | Maximum records to return. Default is `100`; maximum is `500`. |

### Example: search by carrier

```bash
curl "https://air-travel.fastapicloud.dev/v0/flights?carrier=AA&limit=10"
```

### Example: search by carrier and flight number

```bash
curl "https://air-travel.fastapicloud.dev/v0/flights?carrier=AA&flightnumber=100&limit=10"
```

### Example: search by carrier, flight number, and date

```bash
curl "https://air-travel.fastapicloud.dev/v0/flights?carrier=AA&flightnumber=100&flight_date=2024-01-15"
```

### Example: paginate results

```bash
curl "https://air-travel.fastapicloud.dev/v0/flights?carrier=DL&skip=100&limit=100"
```

## Response Shape

The flights endpoint returns a JSON array of flight records.

Important fields include:

| Field | Description |
|---|---|
| `flight_date` | Date of the flight. |
| `iata_code_marketing_airline` | Marketing carrier code. |
| `flight_number_marketing_airline` | Marketing flight number. |
| `origin` | Origin airport code. |
| `origin_city_name` | Origin city name. |
| `dest` | Destination airport code. |
| `dest_city_name` | Destination city name. |
| `crs_dep_time` | Scheduled departure time. |
| `dep_time` | Actual departure time. |
| `crs_arr_time` | Scheduled arrival time. |
| `arr_time` | Actual arrival time. |
| `dep_delay_minutes` | Departure delay in minutes. |
| `arr_delay_minutes` | Arrival delay in minutes. |
| `cancelled` | Cancellation flag, usually `0` or `1`. |
| `diverted` | Diversion flag, usually `0` or `1`. |
| `operating_airline` | Operating airline name or code if available. |
| `iata_code_operating_airline` | Operating airline IATA code if available. |
| `tail_number` | Aircraft tail number if available. |
| `id` | Unique record ID. |

## Basic Usage Guidance for an LLM

When a user asks whether the API is working, call the health check endpoint.

When a user asks for a specific flight, use `/v0/flights` with as many filters as the user provides. Prefer combining `carrier`, `flightnumber`, and `flight_date` when available because that gives the most specific result.

When a user asks for many flights from a carrier or date, use `limit` to control the response size. Do not request more than `500` records at once.

If the user gives a date, format it as `YYYY-MM-DD` before sending it to the API.

If the API returns a validation error, check that:

- `flight_date` uses `YYYY-MM-DD` format.
- `skip` is `0` or greater.
- `limit` is between `1` and `500`.

## Python Example

```python
import requests

BASE_URL = "https://air-travel.fastapicloud.dev"

# Health check
health = requests.get(f"{BASE_URL}/")
health.raise_for_status()
print(health.json())

# Search flights
params = {
    "carrier": "AA",
    "flightnumber": "100",
    "flight_date": "2024-01-15",
    "limit": 10,
}

response = requests.get(f"{BASE_URL}/v0/flights", params=params)
response.raise_for_status()
flights = response.json()
print(flights)
```
