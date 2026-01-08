from abc import ABC, abstractmethod

from fastapi import Depends
from psycopg import Connection
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row

from src.models import User
from src.models.value_objects import UserId
from src.repositories import ActivationCodeRepository, get_activation_code_repository
from src.services.database import get_db

from .exceptions import DuplicateEmailError, UserNotFound


class UserRepository(ABC):
    @abstractmethod
    def save_user(self, user: User) -> User:
        pass

    @abstractmethod
    def select_by_email(self, email: str) -> dict:
        pass

    @abstractmethod
    def update_activated(self, user_id: int) -> None:
        pass


class InMemoryUserRepository(UserRepository):
    users: dict
    last_id: int
    __activation_code_repository: ActivationCodeRepository

    def __init__(
        self,
        activation_code_repository: ActivationCodeRepository,
    ):
        self.users = {}
        self.last_id = 0
        self.__activation_code_repository = activation_code_repository

    def save_user(self, user: User) -> User:
        user_data = user.to_snapshot()
        if user_data.get("email") in self.users:
            raise DuplicateEmailError()
        self.last_id += 1
        user_data["id"] = self.last_id
        user.register(UserId(self.last_id))
        self.users[user_data.get("email")] = user_data
        self.__activation_code_repository.save_activation_code(user)

        return User

    def select_by_email(self, email: str) -> dict:
        user_data = self.users.get(email)
        if not user_data:
            raise UserNotFound()

        return user_data

    def update_activated(self, user_id: int) -> None:
        for email, user in self.users.items():
            if user["id"] == user_id:
                self.users[email]["activated"] = True
                break
        else:
            raise UserNotFound()

    def has_user(self, email: str) -> bool:
        return email in self.users

    def activate(self, email: str) -> None:
        self.users[email]["activated"] = True


class DatabaseUserRepository(UserRepository):
    __conn: Connection
    __activation_code_repository: ActivationCodeRepository

    def __init__(
        self,
        conn: Connection,
        activation_code_repository: ActivationCodeRepository,
    ):
        self.__conn = conn
        self.__activation_code_repository = activation_code_repository

    def save_user(self, user: User) -> User:
        user_data = user.to_snapshot()
        try:
            with self.__conn.cursor() as cursor:
                cursor.execute(
                    """
INSERT INTO users (email, password)
VALUES (%s, %s)
RETURNING id
""",
                    (user_data.get("email"), user_data.get("password")),
                )

                user_id = UserId(cursor.fetchone()[0])
                user.register(user_id)
                self.__activation_code_repository.save_activation_code(user)

                return user
        except UniqueViolation:
            raise DuplicateEmailError(user_data.get("email")) from None

    def select_by_email(self, email: str) -> dict:
        with self.__conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * from users WHERE users.email = %s",
                (email,),
            )
            user = cursor.fetchone()
            if not user:
                raise UserNotFound()

            return user

    def update_activated(self, user_id: int) -> None:
        with self.__conn.cursor() as cursor:
            cursor.execute(
                """
UPDATE users
SET activated = %s
WHERE id = %s
""",
                (True, user_id),
            )


def get_user_repository(
    conn: Connection = Depends(get_db),
    activation_code_repository: ActivationCodeRepository = Depends(
        get_activation_code_repository
    ),
) -> DatabaseUserRepository:
    return DatabaseUserRepository(conn, activation_code_repository)
