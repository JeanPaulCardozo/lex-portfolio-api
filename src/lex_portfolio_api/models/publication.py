from sqlalchemy import Integer, String, ForeignKey, Column, Enum

import enum

from lex_portfolio_api.database import base


class KindType(str, enum.Enum):
    article = "articulo"
    talk = "ponencia"
    book = "libro"
    podcast = "podcast"


class Publication(base):
    __tablename__ = "Publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    kind = Column(Enum(KindType, name="publication_kind_type"))
    venue = Column(String)
    date = Column(String)
    url = Column(String)
    summary = Column(String)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
