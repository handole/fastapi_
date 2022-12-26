import base64
import logging
import pathlib
import tempfile

from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Tuple
from beanie import PydanticObjectId
from beanie import WriteRules
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi import UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager
from fastapi_users import exceptions
from fastapi_users.authentication import Strategy
from fastapi_users.router.common import ErrorCode
from fastapi_users.jwt import generate_jwt

from app import app_settings
from app.model.user import UserLogin
from app.model.user import UserCreate
from app.model.user import User, UserView
from app.model.auth import AccessToken, RefreshToken
from app.utils.authentication import get_hashed_password
from app.utils.authentication import verify_password
from app.utils.authentication import create_access_token, create_refresh_token
from app.utils import query as query_message


router = APIRouter(prefix=f"{app_settings.api_prefix}/users", tags=["Users"])
logger = logging.getLogger("users")


@router.post("/register", response_model=User)
async def register(data: UserCreate, request: Request):
    user = await User.find_one({User.email: data.email})
    if user is not None:
        logger.error(f"{query_message.REGISTER_USER_ALREADY_EXISTS}")
        raise HTTPException(409, "User with that email already exists")
    hashed = get_hashed_password(data.hashed_password)
    usr = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hashed,
        phone_number=data.phone_number
    )
    await usr.create()
    return usr



@router.post("/login")
async def login(
    resp: Response,
    auth: UserLogin
):
    print(auth.email)
    user = await User.find_one(User.email  == auth.email)
    print(verify_password(auth.hashed_password, user.hashed_password))
    if user is None or verify_password(auth.hashed_password, user.hashed_password) is False:
        logger.error("User or email hash been failed")
        raise HTTPException(status_code=401, detail="Bad email or password")

    access_token = create_access_token(subject=auth.email)
    refresh_token = create_refresh_token(subject=auth.email)
    return RefreshToken(access_token=access_token, refresh_token=refresh_token)


@router.get("/users", response_model=List[UserView])
async def users():
    return await User.find(fetch_links=True).to_list()


