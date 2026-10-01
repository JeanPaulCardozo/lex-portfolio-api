from sqlalchemy.orm import Session

from lex_portfolio_api.models.experience import Experience
from lex_portfolio_api.schemas.experience import ExperienceCreate, ExperienceUpdate


def get_experiences(db: Session) -> list[Experience] | None:
    return db.query(Experience).order_by(Experience.start_date.desc()).all()


def get_experience(db: Session, experience_id: int) -> Experience | None:
    return db.query(Experience).filter(Experience.id == experience_id).first()


def create_experience(
    db: Session, experience_schema: ExperienceCreate, user_id: int
) -> Experience:
    new_experience = Experience(
        org=experience_schema.org,
        role=experience_schema.role,
        start_date=experience_schema.start_date,
        end_date=experience_schema.end_date,
        current=experience_schema.current,
        location=experience_schema.location,
        description=experience_schema.description,
        user_id=user_id,
    )

    db.add(new_experience)
    db.commit()
    db.refresh(new_experience)

    return new_experience


def update_experience(
    db: Session, experience_schema: ExperienceUpdate, experience_id: int
) -> Experience:
    experience = get_experience(db, experience_id)
    new_data = experience_schema.model_dump(exclude_unset=True)

    for label, value in new_data.items():
        setattr(experience, label, value)

    db.commit()
    db.refresh(experience)

    return experience


def delete_experience(db: Session, experience_id: int) -> bool:
    experience = get_experience(db, experience_id)

    if experience is None:
        return False
    db.delete(experience)
    db.commit()
    return True
