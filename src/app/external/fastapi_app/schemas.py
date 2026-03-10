from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuthResponse(BaseModel):
    access_token: str
    token_type: str

class AuthRequest(BaseModel):
    email: str = Field(max_length=120)
    password: str = Field(max_length=256)

class AuthTestResponse(BaseModel):
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

