from src.connection import get_db_connection
from src.utils import verify_password


def fetch_user_passwords():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM users ORDER BY id;")
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


def test_seed_stores_hashed_passwords_not_plaintext():
    passwords = fetch_user_passwords()

    assert len(passwords) == 6
    for password in passwords:
        assert password != "password123"
        assert password.startswith("$2b$")


def test_seeded_hashes_match_the_original_passwords():
    for password in fetch_user_passwords():
        assert verify_password("password123", password)