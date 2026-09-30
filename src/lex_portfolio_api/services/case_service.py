from sqlalchemy.orm import Session
from sqlalchemy import or_

from lex_portfolio_api.models.case import Case, CaseResultType
from lex_portfolio_api.schemas.case import CaseCreate, CaseUpdate

from lex_portfolio_api.core.slugify import slugify


def get_cases(
    db: Session,
    user_id: int,
    practice_area_id: int | None = None,
    year: int | None = None,
    result_type: CaseResultType | None = None,
    query: str | None = None,
) -> list[Case]:
    current_query = db.query(Case).filter(Case.user_id == user_id)

    if practice_area_id is not None:
        current_query = current_query.filter(Case.practice_area_id == practice_area_id)

    if year is not None:
        current_query = current_query.filter(Case.year == year)

    if result_type is not None:
        current_query = current_query.filter(Case.result_type == result_type)

    if query is not None:
        needle = f"%{query}%"
        current_query = current_query.filter(
            or_(
                Case.title.ilike(needle),
                Case.role.ilike(needle),
                Case.outcome.ilike(needle),
                Case.situation.ilike(needle),
                Case.action.ilike(needle),
                Case.result.ilike(needle),
            )
        )
    return current_query


def get_case_by_slug(db: Session, slug: str) -> Case | None:
    return db.query(Case).filter(Case.slug == slug).first()


def get_case(db: Session, case_id: int) -> Case | None:
    return db.query(Case).filter(Case.id == case_id).first()


def create_case(db: Session, schema_case: CaseCreate, user_id: int) -> Case:
    new_case = Case(
        slug=slugify(schema_case.title),
        title=schema_case.title,
        practice_area_id=schema_case.practice_area_id,
        year=schema_case.year,
        role=schema_case.role,
        result_type=schema_case.result_type,
        outcome=schema_case.outcome,
        situation=schema_case.situation,
        action=schema_case.action,
        result=schema_case.result,
        skills=schema_case.skills,
        featured=schema_case.featured,
        confidential=schema_case.confidential,
        imageUrl=schema_case.imageUrl,
        user_id=user_id,
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    return new_case


def update_case(db: Session, schema_case: CaseUpdate, case_id: int) -> Case:
    case = get_case(db, case_id)
    new_data = schema_case.model_dump(exclude_unset=True)

    if "title" in new_data:
        new_data["slug"] = slugify(new_data["title"])

    for label, value in new_data.items():
        setattr(case, label, value)

    db.commit()
    db.refresh(case)

    return case


def delete_case(db: Session, case_id: int) -> bool:
    case = get_case(db, case_id)

    if case is None:
        return False

    db.delete(case)
    db.commit()

    return True
