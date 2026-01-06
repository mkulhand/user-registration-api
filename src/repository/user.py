from psycopg import Connection
from psycopg.errors import UniqueViolation

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
