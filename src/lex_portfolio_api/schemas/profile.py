from pydantic import BaseModel, EmailStr, Field
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
    summary: str
    location: str
    email: EmailStr
    notify_email: EmailStr
    phone: str
    whatsapp: str
    linkedin: str
    avatar_url: str
    cv_url: str
    languages: list[str] = []
    bar_admissions: list[str] = []
    education: list[EducationItem] = []
    stats: list[StatItem] = []


class CreateProfile(ProfileBase):
    pass


class UpdateProfile(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    id: int
    user_id: int

    class config:
        from_attributes = True
