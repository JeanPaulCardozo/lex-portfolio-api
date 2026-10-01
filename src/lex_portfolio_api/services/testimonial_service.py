from sqlalchemy.orm import Session

from lex_portfolio_api.models.testimonial import Testimonial
from lex_portfolio_api.schemas.testimonial import (
    TestimonialCreate,
    TestimonialCreateByPublic,
    TestimonialUpdate,
    TestimonialUpdateStatus,
)

from lex_portfolio_api.models.testimonial import StatusType

from datetime import datetime, timezone


def get_testimonials(db: Session) -> list[Testimonial]:
    return (
        db.query(Testimonial)
        .filter(Testimonial.status == StatusType.approved)
        .order_by(Testimonial.created_at.desc())
        .all()
    )


def get_all_testimonials(db: Session, user_id: int) -> list[Testimonial]:
    return (
        db.query(Testimonial)
        .filter(Testimonial.user_id == user_id)
        .order_by(Testimonial.created_at.desc())
        .all()
    )


def get_testimonial(db: Session, testimonial_id: int) -> Testimonial:
    return db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()


def create_testimonial_by_public(
    db: Session, testimonial_schema: TestimonialCreateByPublic, user_id: int
) -> dict[str, bool]:
    new_testimonial = Testimonial(
        author=testimonial_schema.author,
        author_role=testimonial_schema.author_role,
        quote=testimonial_schema.quote,
        rating=testimonial_schema.rating,
        email=testimonial_schema.email,
        status=StatusType.pending,
        created_at=datetime.now(timezone.utc),
        user_id=user_id,
    )

    db.add(new_testimonial)
    db.commit()

    return {"ok": True}


def create_testimonial(
    db: Session, testimonial_schema: TestimonialCreate, user_id: int
) -> Testimonial:
    new_testimonial = Testimonial(
        author=testimonial_schema.author,
        author_role=testimonial_schema.author_role,
        quote=testimonial_schema.quote,
        rating=testimonial_schema.rating,
        email=testimonial_schema.email,
        status=testimonial_schema.status,
        created_at=datetime.now(timezone.utc),
        user_id=user_id,
        context=testimonial_schema.context,
    )

    db.add(new_testimonial)
    db.commit()
    db.refresh(new_testimonial)

    return new_testimonial


def update_testimonial(
    db: Session, testimonial_schema: TestimonialUpdate, testimonial_id: int
) -> Testimonial:
    testimonial = get_testimonial(db, testimonial_id)
    new_data = testimonial_schema.model_dump(exclude_unset=True)

    for label, value in new_data.items():
        setattr(testimonial, label, value)

    db.commit()
    db.refresh(testimonial)

    return testimonial


def update_testimonial_status(
    db: Session, testimonial_schema: TestimonialUpdateStatus, testimonial_id: int
) -> Testimonial:
    testimonial = get_testimonial(db, testimonial_id)
    testimonial.status = testimonial_schema.status

    db.commit()
    db.refresh(testimonial)

    return testimonial


def delete_testimonial(db: Session, testimonial_id: int) -> bool:
    testimonial = get_testimonial(db, testimonial_id)

    if testimonial is None:
        return False

    db.delete(testimonial)
    db.commit()

    return True
