import pytest
from fastapi import BackgroundTasks

from src.models import User
from src.models.exceptions import ValidationError
from src.models.value_objects import Email, Password
from src.repositories import InMemoryActivationCodeRepository, InMemoryUserRepository
from src.services.mail import InMemoryMailAdapter

from .register_user import RegisterUser


def test_register_user_fail_input_validation():
    with pytest.raises(ValidationError) as exc_info:
        Email("testuser")
    assert exc_info.value.infos["prop"] == "email"

    with pytest.raises(ValidationError) as exc_info:
        Password("password123")
    assert exc_info.value.infos["prop"] == "password"


def test_register_user_success_input_validation():
    email = "USER@test.com"
    password = "Password@123"
    user = User(Email(email), Password(password))
    user_data = user.to_snapshot()
    assert user_data.get("email") == email.lower()


@pytest.mark.asyncio
async def test_register_user_execute():
    activation_code_repository = InMemoryActivationCodeRepository()
    user_repository = InMemoryUserRepository(activation_code_repository)
    mail_adapter = InMemoryMailAdapter()
    background_tasks = BackgroundTasks()
    register_user = RegisterUser(
        user_repository,
        mail_adapter,
        background_tasks,
    )

    email = "user@test.com"
    password = "Password@123"
    user = User(Email(email), Password(password))
    register_user.execute(user)

    assert user_repository.has_user(email) == True

    user_data = user.to_snapshot()
    activation_code_repository.has_valid_code(
        user_id=user_data.get("id"), code=user_data.get("activation_code")
    )

    # Simulate end of endpoint execution
    for task in background_tasks.tasks:
        await task()

    assert mail_adapter.has_activation_code_mail(
        email=email, code=user_data.get("activation_code")
    )
