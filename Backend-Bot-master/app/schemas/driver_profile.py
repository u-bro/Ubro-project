from typing import Optional, Any
from pydantic import BaseModel
from datetime import datetime


class DriverProfileCreate(BaseModel):
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    birth_date: Optional[datetime] = None
    photo_url: Optional[str] = None
    license_number: Optional[str] = None
    license_category: Optional[str] = None
    license_issued_at: Optional[datetime] = None
    license_expires_at: Optional[datetime] = None
    experience_years: Optional[int] = None
    approved: Optional[bool] = False
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    qualification_level: Optional[str] = None
    classes_allowed: Optional[dict[str, Any]] = None
    documents_status: Optional[str] = None
    documents_review_notes: Optional[str] = None


class DriverProfileUpdate(DriverProfileCreate):
    user_id: Optional[int] = None


class DriverProfileSchema(DriverProfileCreate):
    id: int
    rating_avg: Optional[int] = None
    rating_count: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
