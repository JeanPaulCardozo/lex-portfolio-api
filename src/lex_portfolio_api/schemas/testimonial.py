from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional

from lex_portfolio_api.models.testimonial import StatusType

from datetime import datetime


class TestimonialBase(BaseModel):
    author: str
    author_role: str
    quote: str
    rating: int = Field(..., ge=1, le=5)
    email: EmailStr


class TestimonialCreateByPublic(TestimonialBase):
    pass


class TestimonialCreate(TestimonialBase):
    context: Optional[str] = None
    status: Optional[StatusType] = StatusType.approved


class TestimonialUpdateStatus(BaseModel):
    status: StatusType


class TestimonialUpdate(TestimonialBase):
    context: Optional[str] = None
    status: StatusType


class TestimonialPublicOut(BaseModel):
    id: int
    author: str
    author_role: str
    quote: str
    rating: int
    context: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TestimonialOut(TestimonialBase):
    id: int
    user_id: int
    context: Optional[str] = None
    status: StatusType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
