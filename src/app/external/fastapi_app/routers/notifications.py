from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from app.core.logger import LogWrapper
from app.interface.notification_service import NotificationService
from app.external.fastapi_app.context import get_notification_service
from .. import schemas
from ..auth_dep import CurrentUser


router = APIRouter()
logger = LogWrapper("notifications").logger


@router.get(
    "",
    response_model=list[schemas.NotificationResponse],
)
async def get_notifications(
    current_user: CurrentUser,
    n_serv: Annotated[NotificationService, Depends(get_notification_service)],
):
    return await n_serv.get_all_notifications_from_user(current_user.id)
