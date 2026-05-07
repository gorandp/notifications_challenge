from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from app.core.logger import LogWrapper
from app.core.user import ROLES as USER_ROLES
from app.core.notification import Notification
from app.interface.channel_service import ChannelService
from app.interface.notification_service import NotificationService
from app.interface.channel_context import ChannelContext
from app.external.fastapi_app.context import (
    get_notification_service,
    get_channel_service,
)
from . import notifications_schemas as schemas
from ..auth_dep import CurrentUser


router = APIRouter()
logger = LogWrapper("notifications").logger


@router.post(
    "",
    response_model=schemas.NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    notification_data: schemas.NotificationCreate,
    current_user: CurrentUser,
    n_serv: Annotated[NotificationService, Depends(get_notification_service)],
    c_serv: Annotated[ChannelService, Depends(get_channel_service)],
):
    c = await c_serv.get_channel(channel_id=notification_data.channel_id)
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )
    n = Notification(
        user_id=current_user.id,
        channel_id=notification_data.channel_id,
        channel_type=c.type,
        status=notification_data.status,
        recipient=notification_data.recipient,
        title=notification_data.title,
        content=notification_data.content,
    )
    channel_ctx = ChannelContext(n_serv)
    try:
        channel_ctx.validate_notification(n)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    n_created = await n_serv.create_notification(n)
    if notification_data.send_after_creating:
        try:
            channel_ctx = ChannelContext(n_serv)
            await channel_ctx.send(c, n_created)
        except Exception:
            pass
    return n_created


@router.get(
    "",
    response_model=list[schemas.NotificationResponse],
)
async def get_notifications(
    current_user: CurrentUser,
    n_serv: Annotated[NotificationService, Depends(get_notification_service)],
):
    ns = await n_serv.get_all_notifications_from_user(current_user.id)
    # if not ns:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Any notifications found",
    #     )
    return ns


@router.get(
    "/{notification_id}",
    response_model=schemas.NotificationResponse,
)
async def get_notification(
    notification_id: int,
    current_user: CurrentUser,
    n_serv: Annotated[NotificationService, Depends(get_notification_service)],
):
    n = await n_serv.get_notification(notification_id)
    # If notification is not found or ownership is not valid while user isn't admin
    if not n or (
        n.user_id != current_user.id and current_user.role != USER_ROLES.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return n


@router.patch(
    "/{notification_id}",
    response_model=schemas.NotificationResponse,
)
async def update_notification_partial(
    current_user: CurrentUser,
    notification_id: int,
    notification_data: schemas.NotificationUpdate,
    n_serv: Annotated[NotificationService, Depends(get_notification_service)],
    c_serv: Annotated[ChannelService, Depends(get_channel_service)],
):
    n = await n_serv.get_notification(notification_id)
    if not n or (
        n.user_id != current_user.id and current_user.role != USER_ROLES.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification_data_u = notification_data.model_dump(exclude_unset=True)

    if "channel_id" in notification_data_u:
        c = await c_serv.get_channel(channel_id=notification_data.channel_id)
        if not c or (
            c.user_id != current_user.id and current_user.role != USER_ROLES.ADMIN
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found",
            )
        channel_id = c.id
        channel_type = c.type

    for k, v in notification_data_u.items():
        if k == "channel_id":
            setattr(n, k, channel_id)
            setattr(n, "channel_type", channel_type)
        else:
            setattr(n, k, v)

    channel_ctx = ChannelContext(n_serv)
    try:
        channel_ctx.validate_notification(n)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    await n_serv.update_notification(notification_id, n)
    return n


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_notification(
    current_user: CurrentUser,
    notification_id: int,
    n_serv: Annotated[NotificationService, Depends(get_notification_service)],
):
    n = await n_serv.get_notification(notification_id)
    if not n or (
        n.user_id != current_user.id and current_user.role != USER_ROLES.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    await n_serv.delete_notification(notification_id)


@router.post(
    "/{notification_id}/send",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def send_notification(
    current_user: CurrentUser,
    notification_id: int,
    n_serv: Annotated[NotificationService, Depends(get_notification_service)],
    c_serv: Annotated[ChannelService, Depends(get_channel_service)],
):
    n = await n_serv.get_notification(notification_id)
    if not n or (
        n.user_id != current_user.id and current_user.role != USER_ROLES.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    try:
        channel = await c_serv.get_channel(channel_id=n.channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found",
            )
        channel_ctx = ChannelContext(n_serv)
        await channel_ctx.send(channel, n)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed sending notification",
        )
