from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=120)
    enabled: bool = Field(default=False)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserCreate(UserBase):
    model_config = ConfigDict(
        from_attributes=True
    )  # so pydantic can read from ORM models

    password: str = Field(max_length=256)
    role: str = Field(max_length=16, default="basic")


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(default=None, max_length=120)
    enabled: bool | None = Field(default=None)
    password: str | None = Field(default=None, max_length=256)
    role: str | None = Field(default=None, max_length=16)
