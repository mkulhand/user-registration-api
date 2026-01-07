from datetime import datetime, timedelta, timezone

from psycopg import Connection


class ActivationCodeRepository:
    conn: Connection

    def __init__(self, conn: Connection):
        self.conn = conn

    def insert(self, user_id: int, code: str) -> int:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
INSERT INTO activation_code (user_id, code)
VALUES (%s, %s)
RETURNING id
""",
                (user_id, code),
            )
            return cursor.fetchone()[0]

    def select_by_code_and_user_id(self, user_id: int, code: str) -> dict:
        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)

        with self.conn.cursor() as cursor:
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
            return cursor.fetchone()
