from typer.testing import CliRunner

from air_travel_cli import __version__
from air_travel_cli.main import app


runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == f"air-travel-cli {__version__}"


def test_health():
    result = runner.invoke(app, ["health"])

    assert result.exit_code == 0
    assert "API is healthy" in result.output


def test_flights():
    result = runner.invoke(
        app,
        [
            "flights",
            "--carrier",
            "AA",
            "--limit",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert "Flight ID:" in result.output or "No flights found." in result.output