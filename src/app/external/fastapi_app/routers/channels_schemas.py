from pydantic import BaseModel, ConfigDict, Field


class ChannelBase(BaseModel):
    type: str = Field(max_length=16)
    resource_url: str = Field(max_length=128)
    port_url: int = Field()


class ChannelCreate(ChannelBase):
    model_config = ConfigDict(from_attributes=True)

    credential_user: str = Field(max_length=128)
    credential_pass: str = Field(max_length=128)


class ChannelResponse(ChannelBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field()
    user_id: int = Field()


class ChannelUpdate(BaseModel):
    type: str | None = Field(default=None, max_length=16)
    resource_url: str | None = Field(default=None, max_length=128)
    port_url: int | None = Field(default=None)
    credential_user: str | None = Field(default=None, max_length=128)
    credential_pass: str | None = Field(default=None, max_length=128)
