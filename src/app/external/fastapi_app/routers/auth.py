from datetime import timedelta
from typing import Annotated
import re

from fastapi import APIRouter, Request, HTTPException, status, Depends
# from fastapi.security import OAuth2PasswordRequestForm

from app.core.logger import LogWrapper
from app.core.user import User
from app.interface.user_service import UserService
from app.external.fastapi_app.context import get_user_service
from . import auth_schemas as schemas
from ..auth_dep import CurrentUser
from ..config import JWTConfig
from ..auth import (
    # oauth2_scheme,
    hash_password,
    verify_password,
    create_access_token,
    # verify_access_token,
)


router = APIRouter()
logger = LogWrapper("auth").logger
# same as channel strategy but tags are disabled
EMAIL_REGEX = re.compile(r"^[\w\d\._-]+@([\w-]+\.)+[\w-]{2,4}$")


@router.post(
    "/token",
    response_model=schemas.AuthResponse,
)
async def login(
    ## Forces FastAPI to create a new thread that can't be created
    ## in Cloudflare Workers
    # form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    u_serv: Annotated[UserService, Depends(get_user_service)],
):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    # logger.info(hash_password(password))
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password required",
        )
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    user = await u_serv.get_user_by_email(username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info("Creating access token success")
    return schemas.AuthResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=schemas.AuthMeResponse,
)
async def get_current_user(
    # token: Annotated[str, Depends(oauth2_scheme)],
    # db: Annotated[Session, Depends(get_db)],
    current_user: CurrentUser,
):
    """Get the currently authenticated user."""
    return current_user


@router.get(
    "/testAuth",
    response_model=schemas.AuthTestResponse,
)
async def test_authentication(
    current_user: CurrentUser,
):
    return {
        "current_user_id": current_user.id,
        "success": True,
    }


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    credentials: schemas.AuthRegister,
    u_serv: Annotated[UserService, Depends(get_user_service)],
):
    if not EMAIL_REGEX.match(credentials.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email",
        )
    u = await u_serv.get_user_by_email(credentials.username)
    if u:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    user = User(
        email=credentials.username,
        password_hash=hash_password(credentials.password),
        enabled=True,
        role="basic",
    )
    await u_serv.create_user(user)
