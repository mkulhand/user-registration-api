import bcrypt
import pytest


@pytest.fixture(autouse=True)
def fake_password_hashing(monkeypatch):
    """Fake bcrypt call for faster test"""

    def fake_hashpw(password: bytes, salt: bytes) -> bytes:
        fake_hash = b"$2b$12$" + b"mJg9A80RpIrewxsxQj71uU" + b"$" + password
        return fake_hash

    monkeypatch.setattr(bcrypt, "hashpw", fake_hashpw)
