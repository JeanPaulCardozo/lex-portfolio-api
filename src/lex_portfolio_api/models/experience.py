from sqlalchemy import Integer, String, ForeignKey, Column, Boolean

from lex_portfolio_api.database import base


class Experience(base):
    __tablename__ = "Experiences"

    id = Column(Integer, primary_key=True, index=True)
    org = Column(String)
    role = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String)
    current = Column(Boolean, default=False)
    location = Column(String)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
