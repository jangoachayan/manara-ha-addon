from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class PairingCode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    expires_at: datetime
    used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(unique=True, index=True)
    device_name: str
    paired_at: datetime = Field(default_factory=datetime.utcnow)