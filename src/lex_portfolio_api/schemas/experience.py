from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import datetime, date


class ExperienceBase(BaseModel):
    org: Optional[str] = None
    role: str = Field(..., min_length=1)
    start_date: str
    end_date: Optional[str] = ""
    current: Optional[bool] = False
    location: Optional[str] = None
    description: Optional[str] = None

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def parse_year_month(cls, value):
        if value is None or value == "":
            return value
        try:
            parsed = datetime.strptime(value, "%Y-%m")
        except ValueError:
            raise ValueError('Invalid format. Use "YYYY-MM" (e.g. "2018-01").')

        if parsed.date() > date.today().replace(day=1):
            raise ValueError("Date cannot be in the future.")

        return parsed.strftime("%Y-%m")


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(ExperienceBase):
    pass


class ExperienceOut(ExperienceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
