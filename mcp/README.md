# Air Travel MCP Server

A lightweight Model Context Protocol (MCP) server built with FastMCP for querying commercial flight data.

This server acts as an MCP wrapper around the Air Travel API and uses the Air Travel Python SDK for all API interactions.

---

## Architecture

```text
MCP Client
     │
     ▼
FastMCP Server
     │
     ▼
Air Travel SDK
     │
     ▼
Air Travel API
     │
     ▼
  PostgreSQL
```

The MCP server does not communicate with the API directly. All requests are made through the Air Travel SDK, allowing the MCP server and CLI to share the same client implementation, request handling, and error handling patterns.

---

## Features

### Flight Search

Search flights using optional filters:

- carrier
- flightnumber
- flight_date
- skip
- limit

Example MCP request:

```python
get_flights(
    carrier="UA",
    flight_date="2025-11-12",
    limit=10
)
```

### Health Check

Verify connectivity to the Air Travel API:

```python
health_check()
```

### Airline Code Lookup

Retrieve airline carrier codes and airline names:

```python
get_airline_codes()
```

or

```python
get_airline_codes(code="AA")
```

---

## Technology Stack

- FastMCP
- Air Travel SDK
- Air Travel API
- FastAPI
- PostgreSQL

---

## Setup

Install dependencies:

```bash
uv sync
```

---

## Run Locally

From the repository root:

```bash
uv run --package air-travel-mcp python mcp/air_travel_server.py
```

---

## Deployment

This project is designed to be deployed to FastMCP Cloud (Prefect Horizon).

The MCP server is packaged as part of a uv workspace and consumes the local Air Travel SDK package directly rather than relying on a published PyPI package.

---

## Related Components

### Air Travel API

Provides flight search and health endpoints backed by PostgreSQL.

### Air Travel SDK

Python client used by both:

- Air Travel CLI
- Air Travel MCP Server

This ensures a consistent integration pattern across client applications.

---

## Purpose

This project demonstrates:

- Building MCP servers with FastMCP
- Reusing a shared SDK across multiple clients
- Wrapping existing REST APIs as MCP tools
- Exposing flight search capabilities to MCP-compatible AI clients