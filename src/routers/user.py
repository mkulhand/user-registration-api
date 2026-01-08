from fastapi import APIRouter, Body, Depends, Response
from fastapi.exceptions import HTTPException

from src.models import User
from src.models.exceptions import ValidationError
from src.models.value_objects import Email, Password
from src.repositories.exceptions import (
    CodeExpired,
    DuplicateEmailError,
    InvalidActivationCode,
)
from src.services import auth
from src.use_cases.activate_user import ActivateUser, get_activate_user_use_case
from src.use_cases.register_user import RegisterUser, get_register_user_use_case

router = APIRouter(prefix="/user", tags=["user"])


@router.post("")
def create_user(
    email: str = Body(...),
    password: str = Body(...),
    register_user: RegisterUser = Depends(get_register_user_use_case),
):
    try:
        user = User(email=Email(email), password=Password(password))
        register_user.execute(user)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.infos)
    except DuplicateEmailError as e:
        raise HTTPException(409, e.detail)

    return Response("User created", 201)


@router.post("/activate")
def activate(
    code: str = Body(..., embed=True),
    user: dict = Depends(auth.get_inactive_user),
    activate_user: ActivateUser = Depends(get_activate_user_use_case),
):
    try:
        activate_user.execute(user.get("id"), code)
    except (CodeExpired, InvalidActivationCode) as e:
        raise HTTPException(409, e.detail)
    return Response("User activated", 200)
