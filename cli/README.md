# Air Travel CLI (v0.2.0)

Command line interface for the Air Travel API.

The CLI is built on top of the Air Travel SDK and provides a simple way to search flight data and check API status directly from the terminal.

## Help

Show available commands:

```bash
air-travel --help
```

Show help for a specific command:

```bash
air-travel flights --help
```

## Version

Display the installed CLI version:

```bash
air-travel --version
```

## Health Check

Check API status:

```bash
air-travel health
```

Example output:

```text
API is healthy
{'message': 'API health check is successful'}
```

## Search Flights

Search by carrier:

```bash
air-travel flights --carrier AA
```

Search by carrier and flight number:

```bash
air-travel flights \
  --carrier AA \
  --flightnumber 100
```

Search by date:

```bash
air-travel flights \
  --flight-date 2025-01-01
```

Limit results:

```bash
air-travel flights \
  --carrier AA \
  --limit 10
```

Skip records:

```bash
air-travel flights \
  --skip 100 \
  --limit 25
```

## JSON Output

Return raw JSON instead of formatted text:

```bash
uv run air-travel flights \
  --carrier AA \
  --json
```

Combine filters with JSON output:

```bash
uv run air-travel flights \
  --carrier UA \
  --flight-date 2025-11-27 \
  --json
```

The JSON output is useful for scripting, automation, and AI coding agents. It can be combined with standard command-line tools such as `jq`:

```bash
uv run air-travel flights \
  --carrier UA \
  --json | jq .
```

Display only the first returned flight:

```bash
uv run air-travel flights \
  --carrier UA \
  --json | jq '.[0]'
```

## Using a Different API Endpoint

Override the default API URL:

```bash
air-travel \
  --base-url http://localhost:8000 \
  health
```

```bash
air-travel \
  --base-url http://localhost:8000 \
  flights --carrier AA
```

```bash
uv run air-travel \
  --base-url http://localhost:8000 \
  flights --carrier AA --json
```

## Typer Features

The CLI is built with Typer, which automatically provides:

```bash
air-travel --help
```

```bash
air-travel health --help
```

```bash
air-travel flights --help
```

along with:

* Automatic help generation
* Type-safe command arguments
* Input validation
* Consistent command-line experience
* Shell completion support

## Relationship to the SDK

The CLI focuses on:

* Command parsing
* Terminal output
* User interaction

The underlying Air Travel SDK handles:

* API communication
* Request construction
* Response processing
* Error handling

This separation keeps the CLI lightweight while making the SDK reusable from Python applications and notebooks.
