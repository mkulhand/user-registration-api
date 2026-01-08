from fastapi import Depends

from src.repositories import (
    ActivationCodeRepository,
    UserRepository,
    get_activation_code_repository,
    get_user_repository,
)


class ActivateUser:
    __user_repo: UserRepository
    __activation_code_repo: ActivationCodeRepository

    def __init__(
        self,
        user_repo: UserRepository,
        activation_repo: ActivationCodeRepository,
    ):
        self.__user_repo = user_repo
        self.__activation_code_repo = activation_repo

    def execute(self, user_id: int, code: str):
        self.__activation_code_repo.has_valid_code(user_id=user_id, code=code)
        self.__user_repo.update_activated(user_id)


def get_activate_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    activation_repo: UserRepository = Depends(get_activation_code_repository),
) -> ActivateUser:
    return ActivateUser(user_repo=user_repo, activation_repo=activation_repo)
