import re

from fastapi import FastAPI, HTTPException
from psycopg2.extras import RealDictCursor
from src.connection import get_db_connection

app = FastAPI(title="BookingManager API")

@app.get("/api/events")
def get_events():
    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Soonest first, as that's what someone browsing events wants to see.
            # id is the tiebreak so events starting together stay in the same order.
            cur.execute("""
                SELECT
                    events.id,
                    events.title,
                    events.starts_at,
                    events.ends_at,
                    NULLIF(CONCAT_WS(', ', venues.name, venues.address), '') AS location
                FROM events
                LEFT JOIN venues ON venues.id = events.venue_id
                ORDER BY events.starts_at, events.id;
            """)
            events = cur.fetchall()

    finally:
        conn.close()

    return {"events": events}

@app.get("/api/events/{event_id}")
def get_event_by_id(event_id: str):
    # Taken as a string because FastAPI would answer a bad int with a 422, and the ticket needs a 400.
    # The digit limit stops absurdly long numbers, which are too big for Python to convert.
    if not re.fullmatch(r"-?[0-9]{1,100}", event_id):
        raise HTTPException(status_code=400, detail="Event id must be an integer")

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    events.id,
                    events.title,
                    events.description,
                    events.starts_at,
                    events.ends_at,
                    venues.name AS location,
                    venues.address,
                    venues.capacity,
                    events.created_at
                FROM events
                LEFT JOIN venues ON venues.id = events.venue_id
                WHERE events.id = %s;
            """, (int(event_id),))
            event = cur.fetchone()

    finally:
        conn.close()

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"event": event}