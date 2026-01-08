from fastapi import BackgroundTasks, Depends

from src.models import User
from src.repositories import UserRepository, get_user_repository
from src.services.mail import EmailAdapter, get_email_adapter


class RegisterUser:
    __user_repo: UserRepository
    __mail_adapter: EmailAdapter
    __background_tasks: BackgroundTasks

    def __init__(
        self,
        user_repo: UserRepository,
        mail_adapter: EmailAdapter,
        background_tasks: BackgroundTasks,
    ):
        self.__user_repo = user_repo
        self.__mail_adapter = mail_adapter
        self.__background_tasks = background_tasks

    def execute(self, user: User):
        self.__user_repo.save_user(user)
        self.__background_tasks.add_task(
            self.__mail_adapter.send_activation_code,
            user,
        )


def get_register_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository),
    mail_adapter: EmailAdapter = Depends(get_email_adapter),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> RegisterUser:
    return RegisterUser(
        user_repo=user_repo,
        mail_adapter=mail_adapter,
        background_tasks=background_tasks,
    )
