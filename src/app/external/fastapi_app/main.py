import os
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
import jwt
from jwt.exceptions import InvalidTokenError

# # from database_models import Base as DbBase
from app.core.logger import LogWrapper
from app.external.database.main import get_db
from app.external.database import database_models as models
from . import schemas
from .config import JWTConfig


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWTConfig.SECRET, algorithm="HS256")
    return encoded_jwt


app = FastAPI()
logger = LogWrapper("main").logger


@app.get("/")
async def home():
    return {"msg": "Hello World!"}


@app.post(
    "/login",
    response_model=schemas.AuthResponse,
)
async def login(data: schemas.AuthRequest, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.email == data.email))
    existing = result.scalars().first()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # HTTP_404_NOT_FOUND
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    password_hash = hashlib.sha256(data.password.encode("utf-8")).hexdigest()
    if password_hash != existing.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        {
            "user_id": existing.id,
            "email": existing.email,
        }
    )
    logger.info("Creating access token success")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get(
    "/testAuth",
    response_model=schemas.AuthTestResponse,
)
async def test_authentication():
    return {
        "success": True,
    }
