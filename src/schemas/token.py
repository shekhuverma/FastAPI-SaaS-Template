from pydantic import BaseModel

from src.schemas import admins


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[admins.Scopes] = []
