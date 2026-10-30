import os
import psycopg2
import json
from pathlib import Path
from psycopg2.extras import execute_values
from src.connection import ENV, get_db_connection

DATA_DIR = Path(__file__).resolve().parent / ("test_data" if ENV == "test" else "data")


def clean_database(cur):
    """1. Remove any data from previous runs."""
    # Functionality will be added in subsequent tickets
    cur.execute("DROP TABLE IF EXISTS rsvps CASCADE;")
    cur.execute("DROP TABLE IF EXISTS events CASCADE;")
    cur.execute("DROP TABLE IF EXISTS users CASCADE;")
    cur.execute("DROP TABLE IF EXISTS venues CASCADE;")

def rebuild_schemas(cur):
    """2. Rebuild the table schemas based on the ERD."""
    # Functionality will be added in subsequent tickets
    cur.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE venues (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            address TEXT,
            capacity INT
        );
    """)

    cur.execute("""
        CREATE TABLE events (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description VARCHAR(255),
            starts_at TIMESTAMPTZ NOT NULL,
            ends_at TIMESTAMPTZ NOT NULL,
            organiser_id INT REFERENCES users(id),
            venue_id INT REFERENCES venues(id),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE rsvps (
        id SERIAL PRIMARY KEY, 
        attendee_id INT REFERENCES users(id), 
        event_id INT REFERENCES events(id), 
        created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)

def insert_test_data(cur):
    """3. Insert the test data."""
    # Functionality will be added in subsequent tickets
    with open(DATA_DIR / "users.json", encoding="utf-8") as f:  # check the real filename
        users = json.load(f)

    execute_values(cur, "INSERT INTO users (email, password, name) VALUES %s;", users, template="(%(email)s, %(password)s, %(name)s)",)

    with open(DATA_DIR / "venues.json", encoding="utf-8") as f: # check the real filename
        venues = json.load(f)

    execute_values(cur, "INSERT INTO venues (name, address, capacity) VALUES %s;", venues, template="(%(name)s, %(address)s, %(capacity)s)",)

    with open(DATA_DIR/ "events.json", encoding="utf-8") as f: # check the real filename 
        events = json.load(f)

    execute_values(
        cur, 
        """INSERT INTO events (title, description, starts_at, ends_at, organiser_id, venue_id)
            VALUES %s;""",
            events,
            template="(%(title)s, %(description)s, %(starts_at)s, %(ends_at)s, %(organiser_id)s, %(venue_id)s)",
        )

    with open(DATA_DIR / "rsvps.json", encoding="utf-8") as f:
        rsvps = json.load(f)
    
    execute_values(
        cur,
        "INSERT INTO rsvps (attendee_id, event_id) VALUES %s;",
        rsvps,
        template="(%(attendee_id)s, %(event_id)s)",
        )

def seed():
    """Main seed function responsible for resetting the database."""
    conn = get_db_connection()
    print("Running seed function...")

    try:
        with conn, conn.cursor() as cur:
            clean_database(cur)
            rebuild_schemas(cur)
            insert_test_data(cur)

    finally:
        conn.close()
    print("Seeding complete")

if __name__ == "__main__":
    seed()