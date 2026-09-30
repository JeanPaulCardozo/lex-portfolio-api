from pydantic import BaseModel, Field
from typing import Optional


class FagsItem(BaseModel):
    q: str
    a: str


class PracticeArea(BaseModel):
    name: str = Field(..., min_length=1)
    summary: Optional[str] = None
    description: Optional[str] = None
    fags: list[FagsItem] = []


class PracticeAreaCreate(PracticeArea):
    pass


class PracticeAreaUpdate(PracticeArea):
    pass


class PracticeAreaOut(PracticeArea):
    id: int
    order: int
    user_id: int
    slug: str

    class Config:
        from_attributes = True
