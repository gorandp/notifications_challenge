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


class NotificationBase(BaseModel):
    title: str = Field(max_length=256)
    body: str = Field(max_length=2048)
    channel_id: str = Field()


class NotificationCreate(NotificationBase):
    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field()
    user_id: int = Field()
