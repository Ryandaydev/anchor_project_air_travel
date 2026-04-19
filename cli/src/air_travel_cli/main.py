import typer
import httpx
from urllib.parse import urljoin

app = typer.Typer()

BASE_URL = "https://air-travel.fastapicloud.dev"


def build_url(path: str) -> str:
    return urljoin(BASE_URL, path)


@app.callback()
def main(
    base_url: str = typer.Option(
        "https://air-travel.fastapicloud.dev",
        "--base-url",
        help="Base URL for the API",
    )
):
    global BASE_URL
    BASE_URL = base_url


@app.command()
def health():
    """Check API health status."""
    try:
        url = build_url("/")
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()

        typer.echo("API is healthy")
        typer.echo(response.json())

    except httpx.HTTPError as e:
        typer.echo(f"Request failed: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def flights(
    carrier: str | None = typer.Option(None, help="Marketing carrier code, e.g. AA"),
    flightnumber: str | None = typer.Option(None, help="Flight number"),
    flight_date: str | None = typer.Option(None, help="Flight date in YYYY-MM-DD format"),
    skip: int = typer.Option(0, help="Number of records to skip"),
    limit: int = typer.Option(100, help="Maximum number of records to return"),
):
    """Search for flights based on carrier, flight number, and flight date."""
    params: dict[str, str | int] = {}

    if carrier:
        params["carrier"] = carrier
    if flightnumber:
        params["flightnumber"] = flightnumber
    if flight_date:
        params["flight_date"] = flight_date

    params["skip"] = skip
    params["limit"] = limit

    url = build_url("/v0/flights")

    try:
        response = httpx.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    except httpx.HTTPStatusError as e:
        typer.echo(f"HTTP ERROR {e.response.status_code}: {e.response.text}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"REQUEST FAILED: {type(e).__name__}: {str(e)}", err=True)
        raise typer.Exit(code=1)

    if not data:
        typer.echo("No flights found.")
        return

    for flight in data:
        typer.echo(
            f"Flight ID: {flight.get('id', 'N/A')}\n"
            f"Date: {flight.get('flight_date', 'N/A')}\n"
            f"Carrier: {flight.get('iata_code_marketing_airline', 'N/A')} {flight.get('flight_number_marketing_airline', 'N/A')}\n"
            f"Route: {flight.get('origin', 'N/A')} ({flight.get('origin_city_name', 'N/A')}) to {flight.get('dest', 'N/A')} ({flight.get('dest_city_name', 'N/A')})\n"
            f"Scheduled Departure: {flight.get('crs_dep_time', 'N/A')}\n"
            f"Actual Departure: {flight.get('dep_time', 'N/A')}\n"
            f"Scheduled Arrival: {flight.get('crs_arr_time', 'N/A')}\n"
            f"Actual Arrival: {flight.get('arr_time', 'N/A')}\n"
            f"Departure Delay: {flight.get('dep_delay_minutes', 'N/A')} minutes\n"
            f"Arrival Delay: {flight.get('arr_delay_minutes', 'N/A')} minutes\n"
            f"Cancelled: {flight.get('cancelled', 'N/A')}\n"
            f"Diverted: {flight.get('diverted', 'N/A')}\n"
            f"Operating Airline: {flight.get('operating_airline', 'N/A')}\n"
            f"Tail Number: {flight.get('tail_number', 'N/A')}\n"
            "---"
        )


def main_entry():
    app()


if __name__ == "__main__":
    main_entry()