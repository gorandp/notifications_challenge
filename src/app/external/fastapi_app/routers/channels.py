from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from app.core.logger import LogWrapper
from app.core.user import ROLES as USER_ROLES
from app.core.channel import Channel
from app.interface.channel_service import ChannelService
from app.external.fastapi_app.context import get_channel_service
from . import channels_schemas as schemas
from ..auth_dep import CurrentUser


router = APIRouter()
logger = LogWrapper("channels").logger


@router.post(
    "",
    response_model=schemas.ChannelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_channel(
    channel_data: schemas.ChannelCreate,
    current_user: CurrentUser,
    c_serv: Annotated[ChannelService, Depends(get_channel_service)],
):
    c = Channel(
        user_id=current_user.id,
        type=channel_data.type,
        credential_user=channel_data.credential_user,
        credential_pass=channel_data.credential_pass,
        resource_url=channel_data.resource_url,
        port_url=channel_data.port_url,
        sender_name=channel_data.sender_name,
    )
    return await c_serv.create_channel(c)


@router.get(
    "",
    response_model=list[schemas.ChannelResponse],
)
async def get_channels(
    current_user: CurrentUser,
    c_serv: Annotated[ChannelService, Depends(get_channel_service)],
):
    cs = await c_serv.get_all_channels(current_user.id)
    return cs


@router.get(
    "/{channel_id}",
    response_model=schemas.ChannelResponse,
)
async def get_channel(
    channel_id: int,
    current_user: CurrentUser,
    c_serv: Annotated[ChannelService, Depends(get_channel_service)],
):
    c = await c_serv.get_channel(channel_id=channel_id)
    if not c or (
        c.user_id != current_user.id and current_user.role != USER_ROLES.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found"
        )
    return c


@router.patch(
    "/{channel_id}",
    response_model=schemas.ChannelResponse,
)
async def update_channel_partial(
    current_user: CurrentUser,
    channel_id: int,
    channel_data: schemas.ChannelUpdate,
    c_serv: Annotated[ChannelService, Depends(get_channel_service)],
):
    c = await c_serv.get_channel(channel_id=channel_id)
    if not c or (
        c.user_id != current_user.id and current_user.role != USER_ROLES.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )

    channel_data_u = channel_data.model_dump(exclude_unset=True)
    channel = Channel(
        **{
            **asdict(c),
            **channel_data_u,
        }
    )
    await c_serv.update_channel(channel_id, channel)
    return channel


@router.delete(
    "/{channel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_channel(
    current_user: CurrentUser,
    channel_id: int,
    c_serv: Annotated[ChannelService, Depends(get_channel_service)],
):
    c = await c_serv.get_channel(channel_id=channel_id)
    if not c or (
        c.user_id != current_user.id and current_user.role != USER_ROLES.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    await c_serv.delete_channel(channel_id)
