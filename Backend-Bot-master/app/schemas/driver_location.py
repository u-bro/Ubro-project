from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class DriverLocationCreate(BaseModel):
    driver_profile_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy_m: Optional[int] = None
    provider: Optional[str] = None
    is_online: Optional[bool] = False
    last_seen_at: Optional[datetime] = None


class DriverLocationUpdate(DriverLocationCreate):
    driver_profile_id: Optional[int] = None


class DriverLocationSchema(BaseModel):
    id: int
    driver_profile_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy_m: Optional[int] = None
    provider: Optional[str] = None
    is_online: bool
    last_seen_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
