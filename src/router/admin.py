from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, Security, status
from fastapi.security import OAuth2PasswordRequestForm

from src.db import services
from src.schemas import admins
from src.security.jwt import create_access_token
from src.security.security import get_current_active_user
from src.security.utils import authenticate_user, get_password_hash
from src.settings import JWTconfig

router = APIRouter(tags=["Admin"])


@router.post("/login")
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[any, Depends(services.save_db)],
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    print("___ USER ___")
    print(user)
    print("___ USER ___")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or Password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Checking whether if user has selected a scope or not
    if form_data.scopes != []:
        # Checking if the user has the provided permissions
        if user.scope not in form_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough Permissions 1",
                headers={"WWW-Authenticate": "Bearer"},
            )

    access_token_expires = timedelta(minutes=JWTconfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


# need to complete this one
@router.post("/Admin/add")
async def add_user(
    db: Annotated[any, Depends(services.save_db)],
    add_admin: admins.CreateAdmin,
    current_user: Annotated[
        any,
        Security(get_current_active_user, scopes=[admins.Scopes.admin]),
    ],
):
    create_admin = admins.AdminInDB(
        username=add_admin.username,
        scope=add_admin.scope,
        hashed_password=get_password_hash(add_admin.password),
    )
    return await services.create_admin(create_admin, db)


@router.delete("/Admin/delete")
async def delete_user(
    db: Annotated[any, Depends(services.save_db)],
    username: str,
    current_user: Annotated[
        any,
        Security(get_current_active_user, scopes=[admins.Scopes.admin]),
    ],
):
    return await services.delete_admin(username, db)
    return await services.delete_admin(username, db)
