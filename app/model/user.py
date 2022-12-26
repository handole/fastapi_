from datetime import datetime
from enum import Enum
from typing import List
from typing import Optional

from beanie import Document
from beanie import Link
from beanie import PydanticObjectId
from fastapi_users import schemas
from fastapi_users.db import BeanieBaseUser
from fastapi_users_db_beanie import BeanieUserDatabase
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import validator
from pymongo import IndexModel
from pymongo.collation import Collation


class BaseUserCreate(BaseModel):
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
                "oauth_accounts",
            },
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class User(Document, BaseUserCreate):
    full_name: Optional[str]
    email: Optional[EmailStr]
    hashed_password: Optional[str]
    phone_number: Optional[str]
    created_on: Optional[datetime] = datetime.now()
    updated_on: Optional[datetime] = datetime.now()

    class Collection:
        name = "users"
        email_collation = Collation("en", strength=2)
        indexes = [
            IndexModel("email", unique=True),
            IndexModel(
                "email", name="case_insensitive_email_index", collation=email_collation
            )
        ]

    class Config:
        schema_extra = {
            "example": {
                "full_name": "test user full",
                "email": "testuser@mail.com",
                "hashed_password": "test123",
                "phone_number": "08111321"
            }
        }
        orm_mode = True


class UserCreate(BaseUserCreate):
    full_name: Optional[str]
    email: EmailStr
    hashed_password: str
    phone_number: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "full_name": "test user full",
                "email": "testuser@mail.com",
                "hashed_password": "test123",
                "phone_number": "08111321"
            }
        }


class UserView(BaseModel):
    full_name: Optional[str]
    email: EmailStr
    hashed_password: str
    phone_number: Optional[str]



class UserLogin(BaseModel):
    email: EmailStr
    hashed_password: str