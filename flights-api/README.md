# Flights API (Async FastAPI Example)

This project demonstrates a minimal **asynchronous FastAPI API backed by
PostgreSQL**.\
It is designed as a teaching example for exploring async patterns in
Python on both the **server (provider)** and **client** sides.

------------------------------------------------------------------------

## Concepts Demonstrated

### Async APIs

The API uses an async stack end‑to‑end:

-   **FastAPI** async endpoints
-   **SQLAlchemy AsyncSession**
-   **asyncpg PostgreSQL driver**

This allows the server to handle many concurrent requests without
blocking during database I/O.

------------------------------------------------------------------------

### Search‑Style API Design

Single flexible endpoint:

    GET /v0/flights

Optional filters:

-   `carrier`
-   `flightnumber`
-   `flight_date`
-   `skip`
-   `limit`

Example:

    /v0/flights?carrier=UA&flight_date=2025-11-12&limit=10

------------------------------------------------------------------------

### Pagination

Pagination uses:

    skip
    limit

Example:

    /v0/flights?skip=100&limit=50

Queries are ordered for stable paging:

    ORDER BY id

------------------------------------------------------------------------

### Fan‑Out / Fan‑In Client Pattern

Because pagination exists, clients can request pages concurrently.

Example fan‑out:

    /v0/flights?skip=0&limit=100
    /v0/flights?skip=100&limit=100
    /v0/flights?skip=200&limit=100

Then combine results after responses return (fan‑in).

This demonstrates how **async clients reduce latency** when calling
APIs.

------------------------------------------------------------------------

## Project Structure

    flights-api/
    ├── main.py
    ├── crud.py
    ├── models.py
    ├── schemas.py
    ├── database.py
    │
    ├── test_crud.py
    ├── test_main.py
    │
    └── pyproject.toml

------------------------------------------------------------------------

## Setup

Install dependencies with **uv**:

    uv sync

Activate the environment (optional):

    source .venv/bin/activate

------------------------------------------------------------------------

## Database

Set the connection string:

    export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/anchor_db"

The project expects an existing **flights** table.

------------------------------------------------------------------------

## Run the API

    uv run fastapi dev main.py

Open the interactive docs:

    http://localhost:8000/docs

------------------------------------------------------------------------

## Run Tests

    uv run pytest

Tests cover:

-   async database queries
-   API behavior
-   pagination correctness
-   ordered paging

------------------------------------------------------------------------

## Purpose

This project is intentionally small.\
It exists to demonstrate:

-   async APIs with FastAPI
-   async PostgreSQL access
-   paginated search endpoints
-   concurrent client request patterns
