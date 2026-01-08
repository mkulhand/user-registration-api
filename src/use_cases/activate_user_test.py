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

    user = User(Email("user@test.com"), Password("Password@123"))
    user_repository.save_user(user)

    yield user, user_repository, activation_code_repository


@pytest.mark.asyncio
async def test_register_user_execute(save_inactive_user):
    user, user_repository, activation_code_repository = save_inactive_user

    activate_user = ActivateUser(
        user_repo=user_repository, activation_repo=activation_code_repository
    )

    user_data = user.to_snapshot()
    activate_user.execute(user_data.get("id"), user_data.get("activationCode"))
    user_data = user_repository.select_by_email(user_data.get("email"))
    assert user_data.get("activated")


@pytest.mark.asyncio
async def test_register_user_bad_code(save_inactive_user):
    user, user_repository, activation_code_repository = save_inactive_user

    activate_user = ActivateUser(
        user_repo=user_repository, activation_repo=activation_code_repository
    )

    user_data = user.to_snapshot()
    with pytest.raises(InvalidActivationCode):
        activate_user.execute(user_data.get("id"), "bad_code")


@pytest.mark.asyncio
async def test_register_user_expired_code(save_inactive_user):
    user, user_repository, activation_code_repository = save_inactive_user

    activate_user = ActivateUser(
        user_repo=user_repository, activation_repo=activation_code_repository
    )
    user_data = user.to_snapshot()
    activation_code_repository.expire_code(user_data.get("id"))

    with pytest.raises(CodeExpired):
        activate_user.execute(user_data.get("id"), user_data.get("activationCode"))
