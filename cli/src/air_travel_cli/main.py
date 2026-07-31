import json

import typer

from air_travel import (
    AirTravelAPIError,
    AirTravelClient,
    AirTravelRequestError,
)
from air_travel_cli import __version__

app = typer.Typer()

client: AirTravelClient


def version_callback(value: bool):
    if value:
        typer.echo(f"air-travel-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        help="Show the CLI version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    base_url: str = typer.Option(
        "https://air-travel.fastapicloud.dev",
        "--base-url",
        help="Base URL for the API",
    ),
):
    global client
    client = AirTravelClient(base_url=base_url)


@app.command()
def health():
    """Check API health status."""
    try:
        response = client.health()

        typer.echo("API is healthy")
        typer.echo(response)

    except AirTravelAPIError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)

    except AirTravelRequestError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)


@app.command()
def flights(
    carrier: str | None = typer.Option(
        None,
        help="Marketing carrier code, e.g. AA",
    ),
    flightnumber: str | None = typer.Option(
        None,
        help="Flight number",
    ),
    flight_date: str | None = typer.Option(
        None,
        help="Flight date in YYYY-MM-DD format",
    ),
    skip: int = typer.Option(
        0,
        help="Number of records to skip",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        min=1,
        help="Maximum number of records to return (default: 20)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output raw JSON instead of formatted text",
    ),
):
    """Search for flights."""
    try:
        data = client.flights(
            carrier=carrier,
            flightnumber=flightnumber,
            flight_date=flight_date,
            skip=skip,
            limit=limit,
        )

    except AirTravelAPIError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)

    except AirTravelRequestError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)

    if not data:
        typer.echo("No flights found.")
        return

    if json_output:
        typer.echo(json.dumps(data, indent=2, default=str))
        return

    for flight in data:
        typer.echo(
            f"Flight ID: {flight.get('id', 'N/A')}\n"
            f"Date: {flight.get('flight_date', 'N/A')}\n"
            f"Carrier: {flight.get('iata_code_marketing_airline', 'N/A')} "
            f"{flight.get('flight_number_marketing_airline', 'N/A')}\n"
            f"Route: {flight.get('origin', 'N/A')} "
            f"({flight.get('origin_city_name', 'N/A')}) "
            f"to {flight.get('dest', 'N/A')} "
            f"({flight.get('dest_city_name', 'N/A')})\n"
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


@app.command()
def carriers(
    code: str | None = typer.Option(
        None,
        help="Airline carrier code, e.g. AA",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output raw JSON instead of formatted text",
    ),
):
    """List airline carrier codes and names."""
    try:
        data = client.carriers(code=code)

    except AirTravelAPIError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)

    except AirTravelRequestError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)

    if not data:
        typer.echo("No carriers found.")
        return

    if json_output:
        typer.echo(json.dumps(data, indent=2, default=str))
        return

    for carrier in data:
        typer.echo(f"{carrier.get('code', 'N/A')}: {carrier.get('name', 'N/A')}")


def main_entry():
    app()


if __name__ == "__main__":
    main_entry()