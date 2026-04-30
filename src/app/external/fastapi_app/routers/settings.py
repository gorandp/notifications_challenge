from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.core.logger import LogWrapper
from app.interface.user_service import UserService
from app.external.fastapi_app.context import get_user_service
from . import settings_schemas as schemas
from ..auth_dep import CurrentUser
from ..auth import hash_password


router = APIRouter()
logger = LogWrapper("settings").logger


@router.get("", response_model=schemas.SettingResponse)
async def get_settings(
    current_user: CurrentUser,
):
    return current_user


@router.patch("", response_model=schemas.SettingResponse)
async def update_settings_partial(
    current_user: CurrentUser,
    user_data: schemas.SettingUpdate,
    u_serv: Annotated[UserService, Depends(get_user_service)],
):
    user_id = current_user.id
    user = await u_serv.get_user(user_id)
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
