from decimal import Decimal
from pydantic import Field
from datetime import datetime
from . import BaseSchema


class UserSchemaCreate(BaseSchema):
    telegram_id: int = Field(None)
    first_name: str | None = Field(None, max_length=100)
    username: str | None = Field(None, max_length=100)
    inviter_id: int | None = Field(None)


class UserSchema(UserSchemaCreate):
    id: int = Field(..., gt=0)
    created_at: datetime | None = Field(None)
    last_active_at: datetime | None = Field(None)
    avatar_url: str | None = Field(None)
    user_phone_number: str | None = Field(None, max_length=20)
    lang_code: str | None = Field(None, max_length=5)
    is_active: bool | None = Field(None)

    balance: float = Field(..., ge=0)
    balance_updated_at: datetime | None = Field(None)

class BalanceUpdateResponse(BaseSchema):
    balance_increase: Decimal = Field(..., description="Amount by which the balance increased")
    new_balance: Decimal = Field(..., description="New balance after the update")

    class Config:
        json_schema_extra = {
            "example": {
                "balance_increase": 150.50,
                "new_balance": 1250.75
            }
        }