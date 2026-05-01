from pydantic import BaseModel, Field


class AuthResponse(BaseModel):
    access_token: str
    token_type: str


class AuthRequest(BaseModel):
    username: str = Field(max_length=120)
    password: str = Field(max_length=256)


class AuthTestResponse(BaseModel):
    current_user_id: int = Field()
    success: bool = Field(default=False)


class AuthRegister(BaseModel):
    username: str = Field(max_length=120)
    password: str = Field(max_length=256)
