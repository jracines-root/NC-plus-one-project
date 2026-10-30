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
uv venv 
```

```bash
uv init --bare
```

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

## Running the API

To start the server, run:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000, with interactive documentation at http://127.0.0.1:8000/docs.

## API Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/events` | Returns all events, ordered by soonest start time |
| GET | `/api/events/:id` | Returns a single event with its venue details. Responds with `404` if the event doesn't exist, or `400` if the id isn't a valid integer |

**Note on `location`:** this value comes from the venue details in the seed data, and its format differs between the two endpoints:

* `/api/events` combines the venue's name and address, which is why it doesn't match the ticket's `Nexus, Leeds, LS2 8PD` example. For example, the first event returns `Nexus, University of Leeds, Discovery Way, Leeds, LS2 3AA`.
* `/api/events/:id` returns only the venue's name, with `address` and `capacity` as separate fields. For example, the first event returns `Nexus, University of Leeds`.

## Running the Tests

The tests use their own database, `nc_plus_one_test`, and their own data in `db/test_data`, so they never touch your development data.

To create or completely reset the test database, run:

```bash
psql -f db/test_setup.sql
```

Create a `.env.test` file in the root directory, in the same format as your development env file but with `DB_NAME=nc_plus_one_test`.

Then run the tests. The test database is re-seeded before every test, so there is no need to seed it yourself:

```bash
uv run pytest
```