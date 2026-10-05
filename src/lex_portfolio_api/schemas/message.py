from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr = Field(..., min_length=1)
    phone: Optional[str] = None
    message: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    read: bool


class MessageOut(MessageBase):
    id: int
    user_id: int
    read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
