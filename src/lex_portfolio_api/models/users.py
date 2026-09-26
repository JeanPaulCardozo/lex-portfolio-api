from sqlalchemy import Integer, String, Column

from lex_portfolio_api.database import base


class User(base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
