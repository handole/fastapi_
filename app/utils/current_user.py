import jwt
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer

from app import auth_settings
from model.auth import TokenData
from model.user import UserView, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could nor validate credentials",
        headers={"WWW-Authentication": "Bearer"}
    )
    try:
        payload = jwt.decode(token, auth_settings.jwt_secret, algorithms=[auth_settings.jwt_algoritm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except Exception as e:
        raise credentials_exception

    try:
        user = await UserView.from_orm(
            User.get(email=token_data.email)
        )
    except Exception as e:
        raise credentials_exception
    
    return user