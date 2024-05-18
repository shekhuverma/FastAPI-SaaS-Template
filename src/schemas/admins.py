from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Scopes(str, Enum):
    admin = "admin"
    edit = "edit"


class Admin(BaseModel):
    username: str
    disabled: bool | None = False
    scope: Optional[Scopes] = None


# To create new admin
class CreateAdmin(Admin):
    password: str


# To store admin in the database
class AdminInDB(Admin):
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)
