from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict

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

class PairRequest(BaseModel):
    pairing_code: str
    device_id: str
    device_name: str

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
    )

class DeviceInfo(BaseModel):
    id: int
    device_id: str
    device_name: str
    paired_at: datetime

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
    )