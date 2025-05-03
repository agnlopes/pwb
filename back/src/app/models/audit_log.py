from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class AuditLog(SQLModel, table=True): # pyright: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID
    action: str
    target_type: str
    target_id: Optional[UUID] = None
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
