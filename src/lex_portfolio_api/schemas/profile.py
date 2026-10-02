from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional


class EducationItem(BaseModel):
    degree: str
    institution: str
    year: str


class StatItem(BaseModel):
    label: str
    value: str


class ProfileBase(BaseModel):
    full_name: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    tagline: str = Field(..., min_length=1)
    headline: str = Field(..., min_length=1)
    summary: Optional[str] = None
    location: Optional[str] = None
    email: Optional[EmailStr] = None
    notify_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    linkedin: Optional[str] = None
    avatar_url: Optional[str] = None
    cv_url: Optional[str] = None
    languages: list[str] = []
    bar_admissions: list[str] = []
    education: list[EducationItem] = []
    stats: list[StatItem] = []

    @field_validator("email", "notify_email", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        return value or None


class CreateProfile(ProfileBase):
    pass


class UpdateProfile(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
