from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import ExpiredSignatureError, JWTError, jwt

from src.db import services
from src.schemas.admins import Admin
from src.schemas.token import TokenData
from src.security.utils import get_user
from src.settings import JWTconfig

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    scopes={
        "admin": "Read/Write/Delete Users and Create Admin",
        "edit": "Read/Write/Delete",
    },
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    security_scopes: SecurityScopes,
    db: Annotated[any, Depends(services.save_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="not allowed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, JWTconfig.SECRET_KEY, algorithms=[JWTconfig.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        # Creating an instance of pydantic model
        token_data = TokenData(username=username, scopes=token_scopes)
        print(token_data)
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session Expired. Please Login Again",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except JWTError as exc:
        raise credentials_exception from exc
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    print(f"token scopes = {token_data.scopes}")
    print(f"security_scopes scopes = {security_scopes.scopes}")

    # If no scope is required by the endpoint return the user
    if security_scopes.scopes == []:
        return user
    else:
        if token_data.scopes == []:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": "bearer"},
            )
        # Checking only first becuase we will always pass only one scope
        elif token_data.scopes[0] not in security_scopes.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": "bearer"},
            )
        return user


async def get_current_active_user(
    current_user: Annotated[Admin, Security(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
