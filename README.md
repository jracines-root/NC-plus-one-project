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