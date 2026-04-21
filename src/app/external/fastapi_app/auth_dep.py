from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.core.user import User
from app.external.fastapi_app.context import user_service_ctx
from .auth import oauth2_scheme, verify_access_token


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    u_serv = user_service_ctx.get()
    user = await u_serv.get_user(user_id_int)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
