import os
import re
import bcrypt


# extra @s anywhere. Deliberately simple: it catches typos, not every rule in the email standard.
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s.]+(\.[^@\s.]+)+")

def hash_password(password):
    """Hash a plaintext password using bcrypt, using a fresh random salt each time."""

    rounds = int(os.environ.get("BCRYPT_ROUNDS", 12))
    salt = bcrypt.gensalt(rounds=rounds)

    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password, hashed):
    """Check a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def hash_user_passwords(users):
    """Return a copy of the users with each plaintext password replaced by its hash."""
    return [{**users, "password": hash_password(user["password"])} for user in users]


def normalise_email(email):
    """Lowercase an email and strip surrounding whitespace, so each address is stored only one way."""
    return email.strip().lower()

def is_valid_email(email):
    """Check that an email looks like a real address, such as name@example.com."""
    return EMAIL_PATTERN.fullmatch(email) is not None