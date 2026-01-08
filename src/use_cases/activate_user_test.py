import pytest

from src.models import User
from src.models.value_objects import Email, Password
from src.repositories import InMemoryActivationCodeRepository, InMemoryUserRepository
from src.repositories.exceptions import CodeExpired, InvalidActivationCode

from .activate_user import ActivateUser


@pytest.fixture
def save_inactive_user():
    activation_code_repository = InMemoryActivationCodeRepository()
    user_repository = InMemoryUserRepository(activation_code_repository)

    user_data = {
        "id": 1,
        "email": "user@test.com",
        "password": "$2b$12$709Gm.lSTLGVujzmjCMC5ekEBh1XR70viGrwccVIiDRq6U6miTvVG",
        "activation_code": "1234",
    }
    user_repository.save_inactive_user(user_data)
    activation_code_repository.save_fake_activation_code(
        user_data.get("id"), user_data.get("activation_code")
    )

    user_data["password"] = "Password@123"

    yield user_data, user_repository, activation_code_repository


def test_activate_user_execute(save_inactive_user):
    user_data, user_repository, activation_code_repository = save_inactive_user

    activate_user = ActivateUser(
        user_repo=user_repository, activation_repo=activation_code_repository
    )

    activate_user.execute(user_data.get("id"), user_data.get("activation_code"))
    user_data = user_repository.select_by_email(user_data.get("email"))
    assert user_data.get("activated")


def test_activate_user_bad_code(save_inactive_user):
    user_data, user_repository, activation_code_repository = save_inactive_user

    activate_user = ActivateUser(
        user_repo=user_repository, activation_repo=activation_code_repository
    )

    with pytest.raises(InvalidActivationCode):
        activate_user.execute(user_data.get("id"), "bad_code")


def test_activate_user_expired_code(save_inactive_user):
    user_data, user_repository, activation_code_repository = save_inactive_user

    activate_user = ActivateUser(
        user_repo=user_repository, activation_repo=activation_code_repository
    )
    activation_code_repository.expire_code(user_data.get("id"))

    with pytest.raises(CodeExpired):
        activate_user.execute(user_data.get("id"), user_data.get("activation_code"))
