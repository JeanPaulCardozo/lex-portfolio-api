from sqlalchemy import Integer, String, DateTime, Boolean, Column, ForeignKey

from lex_portfolio_api.database import base


class Message(base):
    __tablename__ = "Messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    read = Column(Boolean, nullable=False, default=False)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
