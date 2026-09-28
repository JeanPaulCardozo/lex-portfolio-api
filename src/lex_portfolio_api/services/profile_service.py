from sqlalchemy.orm import Session

from lex_portfolio_api.schemas.profile import CreateProfile, UpdateProfile
from lex_portfolio_api.models.profile import Profile


def get_profile(db: Session, user_id: int) -> Profile | None:
    return db.query(Profile).filter(Profile.user_id == user_id).first()


def create_profile(
    db: Session, profile_schema: CreateProfile, current_user_id: int
) -> Profile:
    new_profile = Profile(
        full_name=profile_schema.full_name,
        title=profile_schema.title,
        tagline=profile_schema.tagline,
        headline=profile_schema.headline,
        summary=profile_schema.summary,
        location=profile_schema.location,
        email=profile_schema.email,
        notify_email=profile_schema.notify_email,
        phone=profile_schema.phone,
        whatsapp=profile_schema.whatsapp,
        linkedin=profile_schema.linkedin,
        avatar_url=profile_schema.avatar_url,
        cv_url=profile_schema.cv_url,
        languages=profile_schema.languages,
        bar_admissions=profile_schema.bar_admissions,
        education=profile_schema.education,
        stats=profile_schema.stats,
        user_id=current_user_id,
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


def update_profile(
    db: Session, update_profile_schema: UpdateProfile, user_id: int
) -> Profile:
    profile = get_profile(db, user_id)
    new_info = update_profile_schema.model_dump(exclude_unset=True)

    if profile is None:
        profile = Profile(user_id=user_id, **new_info)
        db.add(profile)

    for field, value in new_info.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile


def delete_profile(db: Session, user_id: int) -> bool:
    profile = get_profile(db, user_id)

    db.delete(profile)
    db.commit()

    return True
