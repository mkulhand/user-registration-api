import pytest


@pytest.fixture(autouse=True)
def real_password_hashing(monkeypatch):
    """Disable fake bcrypt call for router tests"""
    monkeypatch.undo()
    yield
