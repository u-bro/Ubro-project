from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class RideCreate(BaseModel):
    client_id: int
    pickup_address: Optional[str] = None
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    dropoff_address: Optional[str] = None
    dropoff_lat: Optional[float] = None
    dropoff_lng: Optional[float] = None
    scheduled_at: Optional[datetime] = None
    expected_fare: Optional[float] = None
    expected_fare_snapshot: Optional[dict[str, Any]] = None

    @field_validator('scheduled_at', mode='before')
    @classmethod
    def remove_timezone(cls, v):
        """Remove timezone info for naive TIMESTAMP columns"""
        if v is not None and isinstance(v, datetime) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class RideUpdate(BaseModel):
    driver_profile_id: Optional[int] = None
    pickup_address: Optional[str] = None
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    dropoff_address: Optional[str] = None
    dropoff_lat: Optional[float] = None
    dropoff_lng: Optional[float] = None
    scheduled_at: Optional[datetime] = None
    expected_fare: Optional[float] = None
    expected_fare_snapshot: Optional[dict[str, Any]] = None


class RideSchema(BaseModel):
    id: int
    client_id: int
    driver_profile_id: Optional[int] = None
    status: Optional[str] = None
    status_reason: Optional[str] = None
    pickup_address: Optional[str] = None
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    dropoff_address: Optional[str] = None
    dropoff_lat: Optional[float] = None
    dropoff_lng: Optional[float] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    expected_fare: Optional[float] = None
    expected_fare_snapshot: Optional[dict[str, Any]] = None
    driver_fare: Optional[float] = None
    actual_fare: Optional[float] = None
    distance_meters: Optional[int] = None
    duration_seconds: Optional[int] = None
    transaction_id: Optional[int] = None
    commission_id: Optional[int] = None
    is_anomaly: bool
    anomaly_reason: Optional[str] = None
    ride_metadata: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RideStatusChangeRequest(BaseModel):
    to_status: str
    reason: Optional[str] = None
    actor_id: Optional[int] = None
    actor_role: str = Field(..., pattern=r"^(client|driver|system)$")
    meta: Optional[dict[str, Any]] = None
