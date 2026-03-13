# PostgreSQL Setup for the Anchor Project

This project uses PostgreSQL locally inside a GitHub Codespaces / VS Code dev container.

## Why PostgreSQL

PostgreSQL is a better fit than SQLite for demonstrating real async backend behavior in FastAPI:

- better concurrency characteristics
- realistic connection pooling
- production-like SQL database behavior
- works well with SQLAlchemy async + asyncpg

## 1. Update apt

```bash
sudo apt-get update

sudo apt-get install -y postgresql postgresql-contrib

sudo service postgresql start

sudo -u postgres psql
