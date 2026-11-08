# PostgreSQL Setup for the Anchor Project

This project runs PostgreSQL in a Docker container inside a GitHub Codespace / VS Code dev container.

The database setup is contained in the `database/` directory.

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

## 3. Restore the database from the SQL dump

The `anchor_db.sql` file contains the database schema and flight data for the demo.

Restore it into the running PostgreSQL container:

```bash
docker exec -i anchor_postgres   psql -U test_user -d anchor_db   < anchor_db.sql
```

This restores the `airline` schema, the `airline.flights` table, indexes, and data contained in the dump.

---

## 4. Verify the restored data

Check that the flights table exists:

```bash
docker exec -it anchor_postgres   psql -U test_user -d anchor_db   -c "\dt airline.*"
```

Nexgt, verify the number of rows:

```bash
docker exec -it anchor_postgres   psql -U test_user -d anchor_db   -c "SELECT COUNT(*) FROM airline.flights;"
```

You should see the 99,999 flight records returned.

---

## 5. Connect to PostgreSQL manually

To open an interactive PostgreSQL shell:

```bash
docker exec -it anchor_postgres   psql -U test_user -d anchor_db
```

Useful commands:

```sql
\dt airline.*
```

List tables in the `airline` schema.

```sql
\d airline.flights
```

Describe the flights table.

```sql
SELECT COUNT(*) FROM airline.flights;
```

Count flight records.

```sql
\q
```

Exit `psql`.
