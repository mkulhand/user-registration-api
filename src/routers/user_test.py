"""
Note:
On a real prod case, those router integration tests should also mock use case execution to focus solely on router logic.
"""

import base64

import pytest
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient

from main import app
from src.models import User
from src.models.value_objects import Email, Password
from src.repositories import (
    InMemoryActivationCodeRepository,
    InMemoryUserRepository,
    get_user_repository,
)
from src.services.mail import InMemoryMailAdapter
from src.use_cases.activate_user import ActivateUser, get_activate_user_use_case
from src.use_cases.register_user import RegisterUser, get_register_user_use_case

client = TestClient(app)


@pytest.fixture
def mock_register_dependencies():
    activation_code_repository = InMemoryActivationCodeRepository()
    user_repository = InMemoryUserRepository(activation_code_repository)
    mail_adapter = InMemoryMailAdapter()
    background_tasks = BackgroundTasks()
    register_user = RegisterUser(
        user_repository,
        mail_adapter,
        background_tasks,
    )

    def get_register_user():
        return register_user

    overrides = {
        get_register_user_use_case: get_register_user,
    }

    app.dependency_overrides.update(overrides)

    yield

    app.dependency_overrides.clear()


def test_user_creation_success(mock_register_dependencies):
    response = client.post(
        "/api/user", json={"email": "user@test.com", "password": "Test@123"}
    )
    assert response.status_code == 201


def test_user_creation_validation_failure(mock_register_dependencies):
    response = client.post(
        "/api/user", json={"email": "user.com", "password": "Test@123"}
    )
    assert response.status_code == 422
    content = response.json()
    assert content["detail"]["prop"] == "email"

    response = client.post(
        "/api/user", json={"email": "user@test.com", "password": "test"}
    )
    assert response.status_code == 422
    content = response.json()
    assert content["detail"]["prop"] == "password"


@pytest.fixture
def mock_activate_dependencies():
    activation_code_repository = InMemoryActivationCodeRepository()
    user_repository = InMemoryUserRepository(activation_code_repository)

    email = "user@test.com"
    password = "Password@123"
    user = User(Email(email), Password(password))
    user_repository.save_user(user)

    activate_user = ActivateUser(user_repository, activation_code_repository)

    def get_activate_user():
        return activate_user

    def get_mock_user_repository():
        return user_repository

    overrides = {
        get_activate_user_use_case: get_activate_user,
        get_user_repository: get_mock_user_repository,
    }

    app.dependency_overrides.update(overrides)

    user_data = user.to_snapshot()
    yield email, password, user_data.get("activation_code")

    app.dependency_overrides.clear()


def test_user_activation_success(mock_activate_dependencies):
    email, password, code = mock_activate_dependencies
    b64_auth = base64.b64encode(f"{email}:{password}".encode()).decode()
    response = client.post(
        "/api/user/activate",
        json={"code": str(code)},
        headers={"Authorization": f"Basic {b64_auth}"},
    )
    assert response.status_code == 200


def test_user_activate_user_not_found_failure(mock_activate_dependencies):
    email, password, code = mock_activate_dependencies
    b64_auth = base64.b64encode(f"wrong@email.com:{password}".encode()).decode()
    response = client.post(
        "/api/user/activate",
        json={"code": str(code)},
        headers={"Authorization": f"Basic {b64_auth}"},
    )
    assert response.status_code == 404


def test_user_activate_auth_failure(mock_activate_dependencies):
    email, password, code = mock_activate_dependencies
    b64_auth = base64.b64encode(f"{email}:wrong_password".encode()).decode()
    response = client.post(
        "/api/user/activate",
        json={"code": str(code)},
        headers={"Authorization": f"Basic {b64_auth}"},
    )
    assert response.status_code == 401


def test_user_activate_wrong_code_failure(mock_activate_dependencies):
    email, password, code = mock_activate_dependencies
    b64_auth = base64.b64encode(f"{email}:{password}".encode()).decode()
    response = client.post(
        "/api/user/activate",
        json={"code": "wrong_code"},
        headers={"Authorization": f"Basic {b64_auth}"},
    )
    assert response.status_code == 409
