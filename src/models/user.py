import random
import re

from passlib.hash import bcrypt
from psycopg import Connection

from src.repository import ActivationCodeRepository, UserRepository
from src.services.mail import EmailAdapter

from . import ActivationCodeError, ActivationCodeMailError, ValidationError

mail_pattern = r"[^@]+@[^@]+\.[^@]+"
password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~])[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]{8,20}$"


class User:
    conn: Connection
    repository: UserRepository
    id: int | None
    email: str
    password: str
    activated: bool | None

    def __init__(
        self,
        conn: Connection,
        email: str,
        password: str,
        id: int | None = None,
        activated: bool | None = None,
    ):
        self.conn = conn
        self.repository = UserRepository(conn)
        self.id = id
        self.email = email
        self.password = password
        self.activated = activated

    def register(self) -> int:
        self.__validate()
        hashed_password = bcrypt.hash(self.password)
        self.id = self.repository.insert(self.email, hashed_password)

        return self.id

    def send_activation_code(self, mail_adapter: EmailAdapter) -> None:
        code = random.randint(1000, 9999)
        ActivationCodeRepository(self.conn).insert(user_id=self.id, code=str(code))
        if not mail_adapter.send_activation_code(self.email, code):
            raise ActivationCodeMailError()

    def activate(self, code: str) -> None:
        if not ActivationCodeRepository(self.conn).select_by_code_and_user_id(
            user_id=self.id, code=code
        ):
            raise ActivationCodeError()
        self.repository.update_activated(self.id)

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
