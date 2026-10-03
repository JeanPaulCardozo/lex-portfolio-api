from sqlalchemy.orm import Session

from lex_portfolio_api.schemas.profile import CreateProfile, UpdateProfile
from lex_portfolio_api.models.profile import Profile


def get_profile(db: Session) -> Profile | None:
    return db.query(Profile).first()


def update_profile(
    db: Session, update_profile_schema: UpdateProfile, user_id: int
) -> Profile:
    profile = get_profile(db)
    new_info = update_profile_schema.model_dump(exclude_unset=True)

    if profile is None:
        profile = Profile(user_id=user_id, **new_info)
        db.add(profile)

    for field, value in new_info.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile
