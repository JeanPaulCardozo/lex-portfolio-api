from sqlalchemy import Integer, String, ForeignKey, Column, Boolean, Enum
from sqlalchemy.dialects.postgresql import ARRAY

from lex_portfolio_api.database import base

import enum


class CaseResultType(str, enum.Enum):
    judgment = "sentencia"
    settlement = "acuerdo"
    dismissed = "archivo"
    ruling = "dictamen"
    other = "otro"


class Case(base):
    __tablename__ = "Cases"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    role = Column(String)
    result_type = Column(
        Enum(
            CaseResultType,
            name="case_result_type",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    outcome = Column(String, nullable=False)
    situation = Column(String)
    action = Column(String)
    result = Column(String)
    skills = Column(ARRAY(String), default=list)
    featured = Column(Boolean, default=False)
    confidential = Column(Boolean, default=False)
    imageUrl = Column(String, default="")
    practice_area_id = Column(Integer, ForeignKey("PracticeArea.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
