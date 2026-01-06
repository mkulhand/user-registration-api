from fastapi import APIRouter, Body, Depends, Response
from fastapi.exceptions import HTTPException

from src.database import get_db
from src.models import User, ValidationError
from src.repository import DuplicateEmailError

router = APIRouter(prefix="/user", tags=["user"])


@router.post("")
def create_user(
    email: str = Body(...), password: str = Body(...), conn=Depends(get_db)
):
    user = User(conn=conn, email=email, password=password)

    try:
        user.register()
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.infos)
    except DuplicateEmailError as e:
        raise HTTPException(409, e.detail)

    return Response("User created", 201)
