from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from app.core.logger import LogWrapper
from app.core.user import ROLES as USER_ROLES
from app.core.notification import Notification
from app.interface.channel_service import ChannelService
from app.interface.notification_service import NotificationService
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found"
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
    return await n_serv.create_notification(n)


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
    else:
        channel_id = n.channel_id
        channel_type = n.channel_type

    n_status = notification_data.status if "status" in notification_data_u else n.status
    recipient = (
        notification_data.recipient
        if "recipient" in notification_data_u
        else n.recipient
    )
    title = notification_data.title if "title" in notification_data_u else n.title
    content = (
        notification_data.content if "content" in notification_data_u else n.content
    )

    notification = Notification(
        id=n.id,
        user_id=n.user_id,
        channel_id=channel_id,
        channel_type=channel_type,
        status=n_status,
        recipient=recipient,
        title=title,
        content=content,
        inserted_at=n.inserted_at,
    )

    await n_serv.update_notification(notification_id, notification)
    return notification


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
