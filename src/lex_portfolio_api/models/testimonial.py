from sqlalchemy import Integer, String, ForeignKey, Column, Enum, DateTime

import enum

from lex_portfolio_api.database import base


class StatusType(str, enum.Enum):
    pending = "Pendiente"
    approved = "Aprobado"
    rejected = "Rechazado"


class Testimonial(base):
    __tablename__ = "Testimonials"

    id = Column(Integer, primary_key=True, index=True)
    quote = Column(String, nullable=False)
    author = Column(String, nullable=False)
    author_role = Column(String, nullable=False)
    context = Column(String)
    rating = Column(Integer, nullable=False)
    status = Column(Enum(StatusType, name="testimonial_status_type"), nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
