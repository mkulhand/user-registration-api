import base64

import bcrypt
from fastapi import Depends, HTTPException, Request

from src.repositories import UserRepository, get_user_repository
from src.repositories.exceptions import UserNotFound


def _parse_basic_auth(request: Request) -> dict:
    authorization_header = request.headers.get("Authorization")
    try:
        auth_data = authorization_header.split(" ")[1]
        decoded_data = base64.b64decode(auth_data).decode()
        email, password = decoded_data.split(":")
    except:
        raise HTTPException(422, "No BASIC AUTH authentication found")

    return {"email": email, "password": password}


def _get_authenticated_user(
    auth_data: dict = Depends(_parse_basic_auth),
    user_repository: UserRepository = Depends(get_user_repository),
) -> dict:
    try:
        user = user_repository.select_by_email(auth_data["email"])
    except UserNotFound:
        raise HTTPException(404, "User not found")

    if not user or not bcrypt.checkpw(
        auth_data["password"].encode(), user.get("password").encode()
    ):
        raise HTTPException(401, "Couldn't authenticate user")

    return user


def get_active_user(user: dict = Depends(_get_authenticated_user)) -> dict:
    """
    Unused in the project, but this is the way to authenticate users 99% of time.
    """
    if not user.get("activated"):
        raise HTTPException(
            status_code=403, detail="Account not activated. Please check your email."
        )
    return user


def get_inactive_user(user: dict = Depends(_get_authenticated_user)) -> dict:
    """
    Special auth route for users not activated yet (should only be used for /activate route)
    """
    if user.get("activated"):
        raise HTTPException(status_code=400, detail="Account is already activated")
    return user
