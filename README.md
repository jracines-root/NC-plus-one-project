### Project Overview

This project is a **backend REST API for an events platform** that serves as the data layer for a full-stack application. It is designed to handle core business logic, ensure data integrity, and provide a structured JSON interface that a client or frontend can easily consume.

### Core Features

* **User Capabilities:** Register accounts, browse available events, RSVP, and manage personal attendance records.
* **Organiser Capabilities:** Create and manage new events, as well as view comprehensive audience statistics.

### Architectural Context

The application follows a standard three-tier architecture:

1. **Clients (Frontend / Test Suite):** Sends HTTP requests and receives HTTP responses (e.g., web/mobile apps or automated test suites).
2. **REST API (Backend Middle Layer):** Receives incoming requests, processes business logic, enforces security/authentication, manages data integrity, and queries the database.
3. **Database Layer:** A **PostgreSQL database** used for persistent data storage.

### Technologies

* **API:** Python 3.13 and FastAPI
* **Database:** PostgreSQL, connected with psycopg2
* **Testing:** pytest
* **Package management:** uv

## Installation

You will need Python 3.13 or newer, [uv](https://docs.astral.sh/uv/) and PostgreSQL installed. Then install the project's dependencies by running the following command from the root of the project directory:

```bash
uv sync
```

## Database Setup

To create or completely reset your local database environment from scratch, run the following command from the root of the project directory:

```bash
psql -f db/setup.sql
```

## Environment Variables

Create a `.env.development` file in the root directory matching `.env.example` with your local database credentials:

```env
DB_NAME=nc_plus_one
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

`DB_HOST` and `DB_PORT` default to `localhost` and `5432` if left out. `DB_PASSWORD` must be included, but can be left blank if your local PostgreSQL doesn't require one.

## Seeding the Database

To create the tables and load the seed data, run:

```bash
uv run python -m db.seed
```