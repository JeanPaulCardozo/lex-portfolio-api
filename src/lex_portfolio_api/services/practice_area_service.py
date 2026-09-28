from sqlalchemy.orm import Session

from lex_portfolio_api.models.practice_area import PracticeArea
from lex_portfolio_api.schemas.practice_area import (
    PracticeAreaCreate,
    PracticeAreaUpdate,
)

import re
import unicodedata


def get_practice_area(db: Session, practice_area_id: int) -> PracticeArea | None:
    return db.query(PracticeArea).filter(PracticeArea.id == practice_area_id).first()


def get_practice_area_by_slug(
    db: Session, practice_area_slug: str
) -> PracticeArea | None:
    return (
        db.query(PracticeArea).filter(PracticeArea.slug == practice_area_slug).first()
    )


def get_practice_areas(db: Session, user_id: int) -> list[PracticeArea] | None:
    return (
        db.query(PracticeArea)
        .filter(PracticeArea.user_id == user_id)
        .order_by(PracticeArea.order.asc())
        .all()
    )


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = name.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", name).strip("-")


def create_practice_area(
    db: Session, practice_area_schema: PracticeAreaCreate, current_user_id: int
) -> PracticeArea:

    new_practice_area = PracticeArea(
        name=practice_area_schema.name,
        slug=slugify(practice_area_schema.name),
        summary=practice_area_schema.summary,
        description=practice_area_schema.description,
        fags=[item.model_dump() for item in practice_area_schema.fags],
        user_id=current_user_id,
    )

    db.add(new_practice_area)
    db.commit()
    db.refresh(new_practice_area)

    return new_practice_area


def update_practice_area(
    db: Session, practice_area_schema: PracticeAreaUpdate, practice_area_id: int
) -> PracticeArea:

    practice_area = get_practice_area(db, practice_area_id)
    new_info = practice_area_schema.model_dump(exclude_unset=True)

    if "name" in new_info:
        new_info["slug"] = slugify(new_info["name"])

    for field, value in new_info.items():
        setattr(practice_area, field, value)

    db.commit()
    db.refresh(practice_area)

    return practice_area


def delete_practice_area(db: Session, practice_area_id: int) -> bool:
    practice_area = get_practice_area(db, practice_area_id)

    if practice_area is None:
        return False

    db.delete(practice_area)
    db.commit()

    return True
