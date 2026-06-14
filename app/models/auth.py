from __future__ import annotations
from pydantic import BaseModel, ConfigDict

class LoginRequest(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
    )

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    expires_in: int

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
    )

class RefreshRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
    )

class UserPublic(BaseModel):
    id: int
    username: str
    is_active: bool

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
    )