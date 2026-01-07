import os

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.hash import bcrypt

from src.database import get_db
from src.models import User
from src.repository import UserRepository

AUTH_SECRET = os.getenv("AUTH_SECRET").encode()

security_basic = HTTPBasic()


class AuthenticationFailed(Exception):
    detail = "Authentication failed"


def get_authenticated_user(
    token_data: HTTPBasicCredentials = Depends(security_basic), conn=Depends(get_db)
) -> User:
    user = UserRepository(conn).select_by_email(token_data.username)

    if not bcrypt.verify(token_data.password, user.get("password")):
        raise AuthenticationFailed()

    return User(
        conn=conn,
        id=user.get("id"),
        email=user.get("email"),
        password=user.get("password"),
        activated=user.get("activated"),
    )
