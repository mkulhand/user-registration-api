from fastapi import APIRouter, Body, Depends, Response
from fastapi.exceptions import HTTPException

from src.database import get_db
from src.models import (
    ActivationCodeError,
    ActivationCodeMailError,
    User,
    ValidationError,
)
from src.repository import DuplicateEmailError
from src.services import auth
from src.services.mail import EmailAdapter, get_email_adapter

router = APIRouter(prefix="/user", tags=["user"])


@router.post("")
def create_user(
    email: str = Body(...),
    password: str = Body(...),
    conn=Depends(get_db),
    mail_adapter: EmailAdapter = Depends(get_email_adapter),
):
    user = User(conn=conn, email=email, password=password)

    try:
        user.register()
        user.send_activation_code(mail_adapter)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.infos)
    except DuplicateEmailError as e:
        raise HTTPException(409, e.detail)
    except ActivationCodeMailError as e:
        raise HTTPException(502, e.detail)

    return Response("User created", 201)


@router.post("/activate")
def activate(
    code: str = Body(..., embed=True),
    user: User = Depends(auth.get_authenticated_user),
):
    if user.activated:
        raise HTTPException(409, "User is already activated")
    try:
        user.activate(code)
    except ActivationCodeError as e:
        raise HTTPException(409, e.detail)
    return user.id
