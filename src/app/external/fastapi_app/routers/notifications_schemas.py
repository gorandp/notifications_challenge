from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class NotificationBase(BaseModel):
    channel_id: int = Field()
    status: int = Field()
    title: str = Field(max_length=512)
    content: str = Field(max_length=16384)
    recipient: str = Field(max_length=512)


class NotificationCreate(NotificationBase):
    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field()
    user_id: int = Field()
    channel_type: str = Field(max_length=16)
    inserted_at: datetime = Field()


class NotificationUpdate(BaseModel):
    channel_id: int | None = Field(default=None)
    status: int | None = Field(default=None)
    title: str | None = Field(default=None, max_length=512)
    content: str = Field(default=None, max_length=16384)
    recipient: str = Field(default=None, max_length=512)
