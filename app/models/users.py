from psycopg2.extras import RealDictCursor
from src.connection import get_db_connection


def fetch_user_by_email(email):
    """Return the user with this email, including their password hash or none if one does not exist."""
    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, email, password FROM users WHERE email = %s", (email,))
            return cur.fetchone()

    finally:
        conn.close()