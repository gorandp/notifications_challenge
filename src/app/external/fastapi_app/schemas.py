from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuthResponse(BaseModel):
    access_token: str
    token_type: str


class AuthRequest(BaseModel):
    username: str = Field(max_length=120)
    password: str = Field(max_length=256)


class AuthTestResponse(BaseModel):
    current_user_id: int = Field()
    success: bool = Field(default=False)


class UserBase(BaseModel):
    email: str = Field(max_length=120)
    enabled: bool = Field(default=False)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserCreate(UserBase):
    model_config = ConfigDict(from_attributes=True)

    password: str = Field(max_length=256)
    role: str = Field(max_length=16, default="basic")


class UserUpdate(UserBase):
    email: str | None = Field(default=None, max_length=120)
    enabled: bool | None = Field(default=None)
    password: str | None = Field(default=None, max_length=256)
    role: str | None = Field(default=None, max_length=16)


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
