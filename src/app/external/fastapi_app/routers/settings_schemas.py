from pydantic import BaseModel, Field


class SettingResponse(BaseModel):
    email: str = Field(max_length=120)


class SettingUpdate(BaseModel):
    email: str | None = Field(default=None, max_length=120)
    enabled: bool | None = Field(default=None)
    password: str | None = Field(default=None, max_length=256)
