# Anchor Project - Air Travel

Ryan Day's air travel to explore and demonstrate advanced techniques around the me of data science, APIs, and increasingly LLMs.

As I build stuff here, I write about in my Tip Sheet newsletter. Subscribe here to learn how I build these anchor project components and how you can, too: [https://tips.handsonapibook.com/](subscribe to the Tip Sheet newsletter).

This anchor project has some fairly advanced techniques. If you want to build foundational knowledge of FastAPI APIs for AI and Data Science in Python, I wrote a book you should read! Check it out at [https://handsonapibook.com](Hands-on APIs for AI and Data Science: Python Development with FastAPI).

------------------------------------------------------------------------

## Major themes
- Building and using APIs for AI and data science uses
- Using Python asynchronous programming techniques to increase performance and reliability in all areas

------------------------------------------------------------------------

## Architecture Overview

![Anchor Project Architecture](images/anchor_project_big_picture.png)

The diagram above illustrates the major components of the Anchor Project
and how they interact. The **Air Travel SDK** serves as the central
integration layer, allowing multiple consumers to reuse the same
functionality while minimizing duplicated code.

------------------------------------------------------------------------

# Core Components

## Air Travel CLI

A command-line interface designed for developers, analysts, and AI
coding agents.

The CLI provides a convenient way to search and retrieve flight
information directly from the terminal while leveraging the shared SDK
underneath.

**Repository path:**

[cli/](./cli)

------------------------------------------------------------------------

## Air Travel SDK

The central Python package used throughout the project.

The SDK abstracts the underlying API implementation and provides a
consistent interface for multiple consumers.

It is used by:

-   The Air Travel CLI
-   The MCP Server
-   Jupyter notebooks
-   Streamlit and Gradio applications
-   Future integrations

**Repository path:**

[sdk/](./sdk)

------------------------------------------------------------------------

## Flights API

A FastAPI application that exposes flight information through REST
endpoints.

The API acts as the primary access layer for flight data and is consumed
by the SDK.

**Repository path:**

[flights-api/](./flights-api)

------------------------------------------------------------------------

## Air Travel Database

A PostgreSQL/Supabase-backed datastore containing processed airline
operational data.

The Flights API retrieves flight information from this database layer.

**Repository path:**

[postgres/](./postgres)

------------------------------------------------------------------------

## Air Travel MCP Server

An MCP (Model Context Protocol) server that enables AI assistants and
coding agents to interact with the air travel ecosystem through
standardized tooling.

Rather than implementing its own database logic, the MCP server reuses
the shared SDK.

**Repository path:**

[mcp/](./mcp)

------------------------------------------------------------------------

## Ad Hoc Analytics

Jupyter notebooks used for exploratory analysis, experimentation, and
prototyping.

These notebooks demonstrate how analysts can work with the same SDK used
elsewhere in the project.

Typical activities include:

-   Data exploration
-   Feature engineering
-   Hypothesis testing
-   Experimentation

**Repository path:**

[llm/](./llm)

------------------------------------------------------------------------

## Data Applications

Interactive applications built with frameworks such as Streamlit or
Gradio.

These applications provide end-user experiences while relying on the SDK
to retrieve data.

Potential use cases include:

-   Flight search applications
-   Dashboards
-   Demonstrations
-   AI-assisted experiences

**Repository path:**

[llm/](./llm)

------------------------------------------------------------------------

# Data Source

The project uses publicly available airline operational data from the
U.S. Department of Transportation's Bureau of Transportation Statistics
(BTS).

BTS Data Portal:

https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGK&QO_fu146_anzr=b0-gvzr

------------------------------------------------------------------------

# Repository Structure

    anchor_project_air_travel/
    ├── cli/
    ├── data/
    ├── flights-api/
    ├── inference-api/
    ├── llm/
    ├── mcp/
    ├── ml-models/
    ├── postgres/
    └── sdk/

------------------------------------------------------------------------

# Other Anchor Project Pieces

## data/

Supporting datasets, ingestion assets, and intermediate artifacts used
throughout the project.

------------------------------------------------------------------------

## inference-api/

Services related to machine learning inference and deployment
experimentation.

------------------------------------------------------------------------

## llm/

Experiments involving large language models, prompt engineering, and AI
workflows.

------------------------------------------------------------------------

## ml-models/

Machine learning model training, evaluation, and experimentation assets.

------------------------------------------------------------------------

## postgres/

Database infrastructure, schema definitions, and supporting scripts.

------------------------------------------------------------------------

# Getting Started

Clone the repository:

    git clone https://github.com/Ryandaydev/anchor_project_air_travel.git

Explore one of the major entry points:

-   `sdk/` for reusable client functionality
-   `cli/` for command-line workflows
-   `flights-api/` for the REST API implementation
-   `mcp/` for AI agent integrations

------------------------------------------------------------------------

# Design Philosophy

The Anchor Project emphasizes several architectural principles:

-   **One SDK, many consumers** -- shared functionality minimizes
    duplicated logic.
-   **API-first development** -- services communicate through
    well-defined interfaces.
-   **AI-ready architecture** -- MCP servers and agent workflows are
    treated as first-class consumers.
-   **Composable components** -- applications can evolve independently
    while sharing common foundations.
-   **Educational transparency** -- the repository demonstrates
    practical patterns for modern data, API, and AI engineering
    projects.
