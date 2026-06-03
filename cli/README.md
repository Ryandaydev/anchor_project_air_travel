# Air Travel CLI

Command line interface for the Air Travel API.

## Installation

```bash
uv sync
```

## Help

Show available commands:

```bash
uv run air-travel --help
```

Show help for a specific command:

```bash
uv run air-travel flights --help
```

## Health Check

Check API status:

```bash
uv run air-travel health
```

## Search Flights

Search by carrier:

```bash
uv run air-travel flights --carrier AA
```

Search by carrier and flight number:

```bash
uv run air-travel flights \
  --carrier AA \
  --flightnumber 100
```

Search by date:

```bash
uv run air-travel flights \
  --flight-date 2025-01-01
```

Limit results:

```bash
uv run air-travel flights \
  --carrier AA \
  --limit 10
```

Skip records:

```bash
uv run air-travel flights \
  --skip 100 \
  --limit 25
```

## Using a Different API Endpoint

Override the default API URL:

```bash
uv run air-travel \
  --base-url http://localhost:8000 \
  health
```

```bash
uv run air-travel \
  --base-url http://localhost:8000 \
  flights --carrier AA
```

## Typer Features

Typer automatically provides:

```bash
uv run air-travel --help
```

```bash
uv run air-travel health --help
```

```bash
uv run air-travel flights --help
```

along with argument validation, help text, and shell completion support.