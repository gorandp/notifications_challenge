from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, Request, HTTPException, status, Depends
# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import JSONResponse
# from fastapi.security import OAuth2PasswordRequestForm

# from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, select

# import jwt
# from jwt.exceptions import InvalidTokenError

# # from database_models import Base as DbBase
from app.core.logger import LogWrapper
from app.core.user import ROLES as USER_ROLES
from app.core.user import User
from app.external.fastapi_app.context import (
    database_ctx,
    get_user_service,
)
from app.interface.notification_repository import NotificationRepository
from app.interface.notification_service import NotificationService
from app.core.user_service import IUserService
from . import schemas
from .config import JWTConfig
from .auth import (
    oauth2_scheme,
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)
from .auth_dep import CurrentUser


app = FastAPI()
logger = LogWrapper("main").logger


@app.get("/")
async def home():
    return {"msg": "Hello World!"}


@app.post(
    "/token",
    response_model=schemas.AuthResponse,
)
async def login(
    ## Forces FastAPI to create a new thread that can't be created
    ## in Cloudflare Workers
    # form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    u_serv: Annotated[IUserService, Depends(get_user_service)],
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


@app.get("/me")
async def get_current_user(
    # token: Annotated[str, Depends(oauth2_scheme)],
    # db: Annotated[Session, Depends(get_db)],
    current_user: CurrentUser,
):
    """Get the currently authenticated user."""
    return current_user


@app.post(
    "/users",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: schemas.UserCreate,
    current_user: CurrentUser,
    u_serv: Annotated[IUserService, Depends(get_user_service)],
):
    if current_user.role != USER_ROLES.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to create users",
        )
    exists = await u_serv.get_user_by_email(user.email)
    logger.info(f"{user.email}, {exists}")
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User email already in DB",
        )
    pwd = hash_password(user.password)
    u = User(
        email=user.email,
        password_hash=pwd,
        enabled=user.enabled,
        role=user.role,
    )
    u = await u_serv.create_user(u)
    return u


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int,
    current_user: CurrentUser,
    u_serv: Annotated[IUserService, Depends(get_user_service)],
):
    if current_user.role != USER_ROLES.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to get users",
        )
    user = await u_serv.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@app.get("/users", response_model=list[schemas.UserResponse])
async def get_users(
    current_user: CurrentUser,
    u_serv: Annotated[IUserService, Depends(get_user_service)],
):
    if current_user.role != USER_ROLES.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to get users",
        )
    return await u_serv.get_all_users()


@app.get(
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


@app.get(
    "/notifications",
    response_model=list[schemas.NotificationResponse],
)
async def get_notifications(
    current_user: CurrentUser,
):
    notification_repository = NotificationRepository(database_ctx.get())
    notification_service = NotificationService(notification_repository)

    return await notification_service.get_all_notifications_from_user(current_user.id)
