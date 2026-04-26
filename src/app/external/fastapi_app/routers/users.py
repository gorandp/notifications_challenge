from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from app.core.logger import LogWrapper
from app.core.user import ROLES as USER_ROLES
from app.core.user import User
from app.interface.user_service import UserService
from app.external.fastapi_app.context import get_user_service
from .. import schemas
from ..auth_dep import CurrentUser
from ..auth import hash_password


router = APIRouter()
logger = LogWrapper("users").logger


@router.post(
    "",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: schemas.UserCreate,
    current_user: CurrentUser,
    u_serv: Annotated[UserService, Depends(get_user_service)],
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


@router.get("", response_model=list[schemas.UserResponse])
async def get_users(
    current_user: CurrentUser,
    u_serv: Annotated[UserService, Depends(get_user_service)],
):
    if current_user.role != USER_ROLES.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to get users",
        )
    return await u_serv.get_all_users()


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int,
    current_user: CurrentUser,
    u_serv: Annotated[UserService, Depends(get_user_service)],
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


# @router.put("/{user_id}", response_model=schemas.UserResponse)
# async def update_user_full(
#     current_user: CurrentUser,
#     user_id: int,
#     user_data: schemas.UserCreate,
#     u_serv: Annotated[UserService, Depends(get_user_service)],
# ):
#     if current_user.role != USER_ROLES.ADMIN:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="User not allowed to get users",
#         )
#     user = await u_serv.get_user(user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found",
#         )
#     user.email = user_data.email
#     user.enabled = user_data.enabled
#     user.password_hash = hash_password(user_data.password)
#     user.role = user_data.role
#     await u_serv.update_user(user_id, user)
#     return user


@router.patch(
    "/{user_id}",
    response_model=schemas.UserResponse,
)
async def update_user_partial(
    current_user: CurrentUser,
    user_id: int,
    user_data: schemas.UserUpdate,
    u_serv: Annotated[UserService, Depends(get_user_service)],
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
    user_data_u = user_data.model_dump(exclude_unset=True)
    if "email" in user_data_u and user.email != user_data_u.get("email"):
        exists = await u_serv.get_user_by_email(user_data_u["email"])
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
    for k, v in user_data_u.items():
        if k == "password":
            setattr(user, k, hash_password(v))
        else:
            setattr(user, k, v)
    await u_serv.update_user(user_id, user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    current_user: CurrentUser,
    user_id: int,
    u_serv: Annotated[UserService, Depends(get_user_service)],
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
    await u_serv.delete_user(user_id)
