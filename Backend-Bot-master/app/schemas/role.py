from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class RoleCreate(BaseModel):
    code: str
    name: Optional[str] = None
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class RoleSchema(BaseModel):
    id: int
    code: str
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
