from sqlalchemy import Integer, String, ForeignKey, Column, Identity
from sqlalchemy.dialects.postgresql import JSONB

from lex_portfolio_api.database import base


class PracticeArea(base):
    __tablename__ = "PracticeArea"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, index=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    description = Column(String, nullable=False)
    fags = Column(JSONB, default=list)
    order = Column(Integer, Identity(start=1, increment=1), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
