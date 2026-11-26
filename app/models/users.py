from psycopg2.errors import UniqueViolation
from psycopg2.extras import RealDictCursor

from src.connection import get_db_connection


class EmailAlreadyRegistered(Exception):
    """Raised when a new user's email is already taken."""


def fetch_user_by_email(email):
    """Return the user with this email, including their password hash, or None if there isn't one."""
    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, email, password FROM users WHERE email = %s;", (email,))
            return cur.fetchone()

    finally:
        conn.close()


def insert_user(name, email, password_hash):
    """Store a new user and return them, without their password hash."""
    conn = get_db_connection()

    try:
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
                RETURNING id, name, email, created_at;
                """,
                (name, email, password_hash),
            )
            return cur.fetchone()

    # The email column is UNIQUE, so the database itself rejects a duplicate. Relying on it,
    # instead of checking first, also stops two sign-ups with the same email at the same moment.
    except UniqueViolation as e:
        raise EmailAlreadyRegistered(email) from e

    finally:
        conn.close()