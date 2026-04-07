from datetime import datetime, timedelta, UTC

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from .config import JWTConfig

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# def create_access_token_old(data: dict):
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + timedelta(days=7)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(
#         to_encode,
#         JWTConfig.SECRET,
#         algorithm="HS256",
#     )
#     return encoded_jwt


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        JWTConfig.SECRET,
        algorithm=JWTConfig.ALGORITHM,
    )
    return encoded_jwt


def verify_access_token(token: str):
    """Verify a JWT access token and return the subject (user id) if valid"""
    try:
        payload = jwt.decode(
            token,
            JWTConfig.SECRET,
            algorithms=[JWTConfig.ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")
