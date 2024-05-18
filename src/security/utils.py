from passlib.context import CryptContext

from src.db import services
from src.schemas.admins import AdminInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(db, username: str):
    return await services.get_admin(admin_username=username, db=db)


async def authenticate_user(db, username: str, password: str) -> AdminInDB | None:
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
