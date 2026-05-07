from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ChannelBase(BaseModel):
    type: str = Field(max_length=16)
    resource_url: str = Field(max_length=128)
    port_url: int = Field()
    sender_name: str | None = Field(default=None, max_length=128)


class ChannelCreate(ChannelBase):
    model_config = ConfigDict(from_attributes=True)

    credential_user: str = Field(max_length=128)
    credential_pass: str = Field(max_length=128)


class ChannelResponse(ChannelBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field()
    user_id: int = Field()
    inserted_at: datetime = Field()
    updated_at: datetime = Field()


class ChannelUpdate(BaseModel):
    type: str | None = Field(default=None, max_length=16)
    resource_url: str | None = Field(default=None, max_length=128)
    port_url: int | None = Field(default=None)
    credential_user: str | None = Field(default=None, max_length=128)
    credential_pass: str | None = Field(default=None, max_length=128)
    sender_name: str | None = Field(default=None, max_length=128)
