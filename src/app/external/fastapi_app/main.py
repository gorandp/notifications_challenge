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
from app.external.fastapi_app.context import get_session, database_ctx
from app.external.database import database_models as models
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
    u_serv = user_service_ctx.get()
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
