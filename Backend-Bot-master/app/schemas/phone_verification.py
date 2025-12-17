from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class PhoneVerificationCreate(BaseModel):
    user_id: int
    phone: str
    code: str
    expires_at: Optional[datetime] = None
    status: Optional[str] = None
    attempts: Optional[int] = 0


class PhoneVerificationUpdate(BaseModel):
    user_id: Optional[int] = None
    phone: Optional[str] = None
    code: Optional[str] = None
    expires_at: Optional[datetime] = None
    status: Optional[str] = None
    attempts: Optional[int] = None


class PhoneVerificationSchema(BaseModel):
    id: int
    user_id: int
    phone: str
    code: str
    expires_at: Optional[datetime] = None
    status: Optional[str] = None
    attempts: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
