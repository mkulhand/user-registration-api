import re

from passlib.hash import bcrypt
from psycopg import Connection

from src.repository import UserRepository

from . import ValidationError

mail_pattern = r"[^@]+@[^@]+\.[^@]+"
password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~])[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]{8,20}$"


class User:
    email: str
    password: str
    repository: UserRepository

    def __init__(self, conn: Connection, email: str, password: str):
        self.email = email
        self.password = password
        self.repository = UserRepository(conn)

    def register(self) -> int:
        self.__validate()
        hashed_password = bcrypt.hash(self.password)
        return self.repository.insert(self.email, hashed_password)

    def __validate(self) -> None:
        if not re.match(mail_pattern, self.email):
            raise ValidationError(
                infos={"prop": "email", "reason": "invalid mail syntax"}
            )
        if not re.match(password_pattern, self.password):
            raise ValidationError(
                infos={
                    "prop": "password",
                    "reason": (
                        "Password must be 8-20 characters long and contain at least:\n"
                        "• one uppercase letter (A-Z)\n"
                        "• one lowercase letter (a-z)\n"
                        "• one number (0-9)\n"
                        "• one special character: ! @ # $ % ^ & * ( ) _ + - = [ ] { } ; : ' \" , . < > / ? ` ~"
                    ),
                }
            )
