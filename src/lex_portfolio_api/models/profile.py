from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship

from lex_portfolio_api.database import base
from lex_portfolio_api.models.users import User


class Profile(base):
    __tablename__ = "Profiles"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    tagline = Column(String, nullable=False)
    headline = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    location = Column(String, nullable=True)
    email = Column(String, nullable=False)
    notify_email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    cv_url = Column(String, nullable=True)
    languages = Column(ARRAY(String), default=list)
    bar_admissions = Column(ARRAY(String), default=list)
    education = Column(JSONB, default=list)
    stats = Column(JSONB, default=list)

    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)

    user = relationship("User")
