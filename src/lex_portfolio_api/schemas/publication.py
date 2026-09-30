from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional

from lex_portfolio_api.models.publication import KindType


class PublicationBase(BaseModel):
    title: str = Field(..., min_length=1)
    kind: Optional[KindType] = None
    venue: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, value):
        if value is None or value == "":
            return value

        try:
            parsed = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError('Invalid format. Use "YYYY-MM-DD" (e.g. "2018-01-15").')

        if parsed.date() > date.today():
            raise ValueError("Date cannot be in the future.")

        return parsed.strftime("%Y-%m-%d")


class PublicationCreate(PublicationBase):
    pass


class PublicationUpdate(PublicationBase):
    pass


class PublicationOut(PublicationBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
