from typing import Optional, Any
from pydantic import BaseModel
from datetime import datetime


class ChatMessageCreate(BaseModel):
    ride_id: Optional[int] = None
    text: Optional[str] = None
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    message_type: Optional[str] = None
    attachments: Optional[dict[str, Any]] = None
    is_moderated: Optional[bool] = False
    edited_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class ChatMessageUpdate(ChatMessageCreate):
    pass


class ChatMessageSchema(BaseModel):
    id: int
    ride_id: Optional[int] = None
    text: Optional[str] = None
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    message_type: Optional[str] = None
    attachments: Optional[dict[str, Any]] = None
    is_moderated: bool
    created_at: Optional[datetime] = None
    edited_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
