from datetime import timedelta
from pydantic import BaseModel
from typing import Optional

class AccessToken(BaseModel):
    """Access token details"""

    access_token: str
    access_token_expires: timedelta = timedelta(minutes=15)


class RefreshToken(AccessToken):
    """Access and refresh token details"""

    refresh_token: str
    refresh_token_expires: timedelta = timedelta(days=30)


class TokenData(BaseModel):
    email: Optional[str] = None
    