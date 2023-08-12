from datetime import datetime
from typing import List
from typing import Optional

from beanie import Document
from beanie import PydanticObjectId
from pydantic import BaseModel
from pydantic import Field

from user import User


class Author(User, Document):
    aliases: str
    bio: Optional[str]
    pic: Optional[str]
    