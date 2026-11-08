# Manual Datbase Creation

If you want to perform the step-by-step loading of the database you can follow these instructions.

Unless otherwise noted, run the PostgreSQL setup commands from the `database/` directory:

```bash
cd database
```

## Why this setup

Using PostgreSQL in Docker keeps the database isolated from the Codespace environment while still making it easy to run locally.

This approach provides:

- reproducible database setup with Docker Compose
- PostgreSQL 16
- persistent storage through a Docker volume
- a production-like PostgreSQL environment
- compatibility with SQLAlchemy async + `asyncpg`
- simple reset and rebuild commands

The credentials shown below are development/demo credentials for the local Codespace database and should not be used in production.

---

## 1. Docker Compose configuration

The `database/docker-compose.yml` file contains:

```yaml
services:
  postgres:
    image: postgres:16
    container_name: anchor_postgres
    restart: unless-stopped

    environment:
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
      POSTGRES_DB: anchor_db

    ports:
      - "5432:5432"

    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

The PostgreSQL connection settings are:

```text
host: localhost
port: 5432
database: anchor_db
user: test_user
password: test_password
```

---

## 2. Start PostgreSQL

From the `database/` directory:

```bash
docker compose up -d
```

Check that the container is running:

```bash
docker compose ps
```

The status should show `Up`.

Example:

```text
NAME              IMAGE         SERVICE    STATUS
anchor_postgres   postgres:16   postgres   Up
```

---

## 3. Create the database schema

The SQL scripts use the `airline` schema, so create it first:

```bash
docker exec -i anchor_postgres   psql -U test_user -d anchor_db   < load/schema.sql
```

---

## 4. Create the staging table

Run:

```bash
docker exec -i anchor_postgres   psql -U test_user -d anchor_db   < load/stage_flights.sql
```

This creates:

```text
airline.stage_flights
```

The staging table stores incoming CSV values as text so the raw BTS data can be loaded before type conversion.

---

## 5. Create the final flights table

Run:

```bash
docker exec -i anchor_postgres   psql -U test_user -d anchor_db   < load/flights.sql
```

This creates:

```text
airline.flights
```

It also creates indexes used by the API for common flight searches.

Verify both tables:

```bash
docker exec -it anchor_postgres   psql -U test_user -d anchor_db   -c "\dt airline.*"
```

You should see:

```text
airline | flights
airline | stage_flights
```

---

## 6. Copy the CSV file into the PostgreSQL container

From the `database/` directory:

```bash
docker cp load/loading_file.csv anchor_postgres:/tmp/loading_file.csv
```

This makes the CSV available inside the PostgreSQL container.

---

## 7. Load the CSV into the staging table

Connect to PostgreSQL:

```bash
docker exec -it anchor_postgres   psql -U test_user -d anchor_db
```

Then run:

```sql
\copy airline.stage_flights FROM '/tmp/loading_file.csv' CSV HEADER;
```

Check the staging row count:

```sql
SELECT COUNT(*) FROM airline.stage_flights;
```

Exit:

```sql
\q
```

---

## 8. Transform staging data into the final table

Run:

```bash
docker exec -i anchor_postgres   psql -U test_user -d anchor_db   < load/load_script.sql
```

`load_script.sql` inserts rows from `airline.stage_flights` into `airline.flights` and converts text values into the appropriate PostgreSQL types.

> **Important:** `load_script.sql` appends records to `airline.flights`. Running it more than once without recreating or clearing the final table will create duplicate records.

---

## 9. Verify the final data

Check the number of loaded flight records:

```bash
docker exec -it anchor_postgres   psql -U test_user -d anchor_db   -c "SELECT COUNT(*) FROM airline.flights;"
```

Inspect a few rows:

```bash
docker exec -it anchor_postgres   psql -U test_user -d anchor_db   -c "
SELECT
    id,
    flight_date,
    iata_code_marketing_airline,
    flight_number_marketing_airline,
    origin,
    dest
FROM airline.flights
LIMIT 10;
"
```

---


## Common PostgreSQL commands

Connect to the database:

```bash
docker exec -it anchor_postgres   psql -U test_user -d anchor_db
```

Inside `psql`:

```sql
\dt
```

List tables in the current schema.

```sql
\dt airline.*
```

List tables in the `airline` schema.

```sql
\d airline.flights
```

Describe the final flights table.

```sql
SELECT COUNT(*) FROM airline.flights;
```

Count flight records.

```sql
\q
```

Exit `psql`.

---

## Stop PostgreSQL

From the `database/` directory, stop and remove the container while preserving the database volume:

```bash
docker compose down
```

Start it again later:

```bash
docker compose up -d
```