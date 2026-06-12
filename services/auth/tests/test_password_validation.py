import hashlib

from src.services.login import validate_password


def test_validate_password_accepts_users_service_sha256_hash():
    password = "Admin123!"
    stored = hashlib.sha256(password.encode("utf-8")).hexdigest()

    assert validate_password(password, stored) is True
