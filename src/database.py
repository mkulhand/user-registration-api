import os

import psycopg_pool
from psycopg import Connection

DB_LOGIN = os.getenv("DB_LOGIN")
DB_PASSWORD = os.getenv("DB_PASSWORD")

pool = psycopg_pool.ConnectionPool(
    conninfo=os.getenv("DB_URL"),
    min_size=4,
    max_size=20,
    timeout=30,
)


def get_db():
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def check_db_connection(conn: Connection):
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print("PostgreSQL version:", version[0])


def initialize_db(conn: Connection):
    with conn.cursor() as cur:
        cur.execute(
            """
CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL           PRIMARY KEY,
    email       VARCHAR(255)        NOT NULL UNIQUE,
    password    VARCHAR(255)        NOT NULL,
    activated   BOOLEAN             NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS activation_code (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    code VARCHAR(4) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
"""
        )
        conn.commit()


conn = pool.getconn()
try:
    check_db_connection(conn)
    initialize_db(conn)
except Exception as e:
    print(e)
    # Override Exception to avoid any secrets logged
    raise Exception("Error initializing database")
finally:
    pool.putconn(conn)
