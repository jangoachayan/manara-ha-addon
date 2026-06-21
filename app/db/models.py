from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint

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

class EntityGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    display_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GroupMembership(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('group_id', 'entity_id'),)

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key='entitygroup.id', index=True)
    entity_id: str = Field(index=True)
    display_order: int = Field(default=0)
