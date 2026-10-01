from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from lex_portfolio_api.models.case import CaseResultType


class CaseBase(BaseModel):
    title: str
    practice_area_id: int
    year: int
    role: Optional[str] = None
    result_type: CaseResultType
    outcome: str
    situation: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    skills: list[str] = []
    featured: Optional[bool] = False
    confidential: Optional[bool] = False
    imageUrl: Optional[str] = None


class CaseCreate(CaseBase):
    pass


class CaseUpdate(CaseBase):
    pass


class CaseOut(CaseBase):
    id: int
    user_id: int
    slug: str

    model_config = ConfigDict(from_attributes=True)
