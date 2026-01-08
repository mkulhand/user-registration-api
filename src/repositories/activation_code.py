from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from fastapi import Depends
from psycopg import Connection

from src.models import User
from src.services.database import get_db

from .exceptions import CodeExpired, InvalidActivationCode


class ActivationCodeRepository(ABC):
    @abstractmethod
    def save_activation_code(self, user: User) -> User:
        pass

    @abstractmethod
    def has_valid_code(self, user_id: int, code: str) -> None:
        pass


class InMemoryActivationCodeRepository(ActivationCodeRepository):
    activation_codes: dict

    def __init__(self):
        self.activation_codes = {}

    def save_activation_code(self, user: User) -> None:
        user_data = user.to_snapshot()
        self.activation_codes[user_data.get("id")] = {
            "activation_code": user_data.get("activation_code"),
            "created_at": datetime.now(timezone.utc),
        }

    def has_valid_code(self, user_id: int, code: str) -> None:
        data = self.activation_codes.get(user_id)
        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)

        if not data or data["activation_code"] != code:
            raise InvalidActivationCode()
        if data["created_at"] < one_minute_ago:
            raise CodeExpired()

    def expire_code(self, user_id: int) -> None:
        self.activation_codes[user_id]["created_at"] = datetime.now(
            timezone.utc
        ) - timedelta(hours=1)

    def save_fake_activation_code(self, user_id: int, code: str) -> None:
        self.activation_codes[user_id] = {
            "activation_code": code,
            "created_at": datetime.now(timezone.utc),
        }


class DatabaseActivationCodeRepository(ActivationCodeRepository):
    __conn: Connection

    def __init__(self, conn: Connection):
        self.__conn = conn

    def save_activation_code(self, user: User) -> None:
        with self.__conn.cursor() as cursor:
            user_data = user.to_snapshot()
            cursor.execute(
                """
INSERT INTO activation_code (user_id, code)
VALUES (%s, %s)
RETURNING id
""",
                (user_data.get("id"), user_data.get("activation_code")),
            )
            return cursor.fetchone()[0]

    def has_valid_code(self, user_id: int, code: str) -> None:
        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)

        with self.__conn.cursor() as cursor:
            cursor.execute(
                """
SELECT 1 from activation_code
WHERE activation_code.user_id = %s
    AND activation_code.code = %s
    AND created_at >= %s
LIMIT 1
""",
                (user_id, code, one_minute_ago),
            )
            if not cursor.fetchone():
                raise InvalidActivationCode()


def get_activation_code_repository(
    conn: Connection = Depends(get_db),
) -> DatabaseActivationCodeRepository:
    return DatabaseActivationCodeRepository(conn)
