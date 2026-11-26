from src.utilis import hash_password, hash_user_passwords, verify_password


def test_hash_password_does_not_return_the_plaintext():
    assert hash_password("password123") != "password123"


def test_hash_password_returns_a_bcrypt_hash():
    assert hash_password("password123").startswith("$2b$")


def test_hash_password_gives_a_different_hash_each_time():
    # bcrypt adds a random salt, so two users with the same password don't share a hash
    assert hash_password("password123") != hash_password("password123")


def test_verify_password_accepts_the_correct_password():
    hashed = hash_password("password123")

    assert verify_password("password123", hashed) is True


def test_verify_password_rejects_an_incorrect_password():
    hashed = hash_password("password123")

    assert verify_password("wrongpassword", hashed) is False


def test_hash_user_passwords_returns_an_empty_list_for_no_users():
    assert hash_user_passwords([]) == []


def test_hash_user_passwords_replaces_each_password_with_its_hash():
    users = [
        {"name": "Alice", "email": "alice@example.com", "password": "password123"},
        {"name": "Bob", "email": "bob@example.com", "password": "hunter2"},
    ]

    result = hash_user_passwords(users)

    assert verify_password("password123", result[0]["password"])
    assert verify_password("hunter2", result[1]["password"])


def test_hash_user_passwords_keeps_the_other_fields():
    users = [{"name": "Alice", "email": "alice@example.com", "password": "password123"}]

    result = hash_user_passwords(users)

    assert result[0]["name"] == "Alice"
    assert result[0]["email"] == "alice@example.com"
    assert set(result[0].keys()) == {"name", "email", "password"}


def test_hash_user_passwords_does_not_change_the_input():
    users = [{"name": "Alice", "email": "alice@example.com", "password": "password123"}]

    hash_user_passwords(users)

    assert users == [{"name": "Alice", "email": "alice@example.com", "password": "password123"}]