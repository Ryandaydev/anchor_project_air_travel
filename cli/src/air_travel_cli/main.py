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
    """
    Air Travel CLI
    """
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
def flights():
    """Flights endpoint (placeholder)."""
    typer.echo("Flights command coming soon...")

def main_entry():
    app()


if __name__ == "__main__":
    main_entry()