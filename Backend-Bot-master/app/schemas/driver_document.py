from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class DriverDocumentCreate(BaseModel):
    driver_profile_id: int
    doc_type: str
    file_url: str
    status: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None


class DriverDocumentUpdate(BaseModel):
    driver_profile_id: Optional[int] = None
    doc_type: Optional[str] = None
    file_url: Optional[str] = None
    status: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None


class DriverDocumentSchema(BaseModel):
    id: int
    driver_profile_id: int
    doc_type: str
    file_url: str
    status: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
