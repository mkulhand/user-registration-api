from psycopg import Connection
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row

from . import DuplicateEmailError


class UserRepository:
    conn: Connection

    def __init__(self, conn: Connection):
        self.conn = conn

    def insert(self, email: str, password: str) -> int:
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
INSERT INTO users (email, password)
VALUES (%s, %s)
RETURNING id
""",
                    (email, password),
                )
                return cursor.fetchone()[0]
        except UniqueViolation:
            raise DuplicateEmailError(email) from None

    def select_by_email(self, email: str) -> dict | None:
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * from users WHERE users.email = %s",
                (email,),
            )
            return cursor.fetchone()

    def update_activated(self, user_id: int) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
UPDATE users
SET activated = %s
WHERE id = %s
""",
                (True, user_id),
            )
