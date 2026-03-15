# Flight Delay Inference API

This folder contains a reference implementation of an **asynchronous
machine learning inference service** built with Python. It is part of
the Anchor Project and demonstrates how to expose trained models through
a production-style API using FastAPI, PostgreSQL, background jobs, and
webhook notifications.

The service predicts **arrival delay distributions for airlines** using
quantile regression models. Instead of returning a single number, the
API returns three predictions representing the **10th, 50th, and 90th
percentile delay**. This allows clients to understand typical delays as
well as the risk of larger delays.

The machine learning models themselves are stored separately in the
project under:

    /ml-models/

See the documentation there for details on model training, inputs, and
exported ONNX artifacts:

    /ml-models/readme.md

------------------------------------------------------------------------

# Project Structure

The inference API code in this folder is organized into several small
modules to keep the application easy to maintain.

    inference-api/
    │
    ├── flights_inference_api_main.py
    ├── schemas.py
    ├── models.py
    ├── database.py
    ├── crud.py
    ├── flight_inference_jobs.sql
    └── webhook_receiver.py

### flights_inference_api_main.py

This is the main FastAPI application.

It defines the API endpoints used to:

-   submit inference jobs
-   check job status
-   retrieve prediction results

The API follows a **job-based asynchronous pattern**:

1.  Client submits a job
2.  API returns a `job_id`
3.  Background task performs inference
4.  Client polls for results or receives a webhook notification

The inference logic loads the ONNX models and runs predictions for the
requested airline.

Run the API with:

    uvicorn flights_inference_api_main:app --reload

------------------------------------------------------------------------

### schemas.py

Defines **Pydantic models** used by the API.

These schemas validate:

-   request payloads
-   API responses
-   prediction outputs

Using schemas keeps request validation separate from the API routing
logic and provides automatic OpenAPI documentation.

------------------------------------------------------------------------

### models.py

Defines the **SQLAlchemy ORM model** representing inference jobs stored
in the database.

Each job record stores:

-   job_id
-   job status
-   request payload
-   prediction results
-   timestamps
-   optional webhook URL

This allows the API to persist jobs and track their lifecycle.

------------------------------------------------------------------------

### database.py

Handles **PostgreSQL connectivity** using async SQLAlchemy.

It defines:

-   the async database engine
-   session factory
-   dependency for FastAPI endpoints

The connection string is typically provided through an environment
variable:

    DATABASE_URL

Example:

    postgresql+asyncpg://user:password@localhost:5432/anchor_db

------------------------------------------------------------------------

### crud.py

Contains database helper functions used by the API.

Examples include:

-   creating inference jobs
-   updating job status
-   storing results
-   retrieving job records

Keeping database logic here prevents the main API file from becoming
cluttered with SQL or ORM queries.

------------------------------------------------------------------------

### flight_inference_jobs.sql

This file contains the SQL script used to create the database table
required by the API.

The table stores all inference job metadata and results.

Create the table with:

    psql "$PG_URL" -f flight_inference_jobs.sql

The API expects this table to exist before startup.

------------------------------------------------------------------------

# Webhook Receiver

The project includes a simple webhook receiver used to test
**event-driven inference workflows**.

The webhook service exposes an endpoint that receives notifications when
an inference job completes.

Example endpoint:

    POST /flight-inference-webhook

When the inference API finishes processing a job, it can send the
prediction results to this endpoint.

Run the webhook receiver with:

    uvicorn webhook_receiver:app --reload --port 9000

Then include the webhook URL when submitting a job:

    http://localhost:9000/flight-inference-webhook

This allows external systems to receive results automatically instead of
polling the API.

------------------------------------------------------------------------

# Example Inference Workflow

1.  Submit a job

```{=html}
<!-- -->
```
    POST /inference-jobs

Request body:

    {
      "Marketing_Airline_Network": "DL"
    }

Response:

    {
      "job_id": "uuid",
      "status": "queued"
    }

------------------------------------------------------------------------

2.  Check job status

```{=html}
<!-- -->
```
    GET /inference-jobs/{job_id}

------------------------------------------------------------------------

3.  Retrieve prediction results

```{=html}
<!-- -->
```
    GET /inference-jobs/{job_id}/result

Example output:

    {
      "p10_delay_minutes": -2,
      "p50_delay_minutes": 4,
      "p90_delay_minutes": 32
    }

------------------------------------------------------------------------

# Running the System Locally

1.  Start PostgreSQL

2.  Create the job table

```{=html}
<!-- -->
```
    psql "$PG_URL" -f flight_inference_jobs.sql

3.  Start the inference API

```{=html}
<!-- -->
```
    uvicorn flights_inference_api_main:app --reload

4.  Start the webhook receiver (optional)

```{=html}
<!-- -->
```
    uvicorn webhook_receiver:app --reload --port 9000

------------------------------------------------------------------------

# Purpose

This inference API demonstrates several patterns common in modern ML
systems:

-   asynchronous FastAPI services
-   ONNX model serving
-   PostgreSQL-backed job storage
-   background task execution
-   webhook-based result notifications

The goal is to provide a **clear, minimal example of a production-style
inference architecture** that Python developers can explore and extend
as part of the Anchor Project.
