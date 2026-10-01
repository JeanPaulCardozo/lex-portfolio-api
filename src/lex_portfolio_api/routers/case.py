from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.orm import Session

from lex_portfolio_api.database import get_db
from lex_portfolio_api.models.case import Case
from lex_portfolio_api.models.users import User
from lex_portfolio_api.core.dependencies import get_current_user
from lex_portfolio_api.schemas.case import CaseOut, CaseCreate, CaseUpdate
from lex_portfolio_api.services import case_service
from lex_portfolio_api.core.slugify import slugify
from lex_portfolio_api.models.case import CaseResultType

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/", response_model=list[CaseOut], status_code=200)
def list_cases(
    practice_area_id: int = None,
    year: int = None,
    result_type: CaseResultType = None,
    query: str = None,
    db: Session = Depends(get_db),
):
    return case_service.get_cases(db, practice_area_id, year, result_type, query)


@router.get("/{slug}", response_model=CaseOut, status_code=200)
def get_case_by_slug(slug: str, db: Session = Depends(get_db)):
    case = case_service.get_case_by_slug(db, slug)

    if case is None:
        raise HTTPException(status_code=404, detail="Case Not Found")

    return case


@router.post("/", response_model=CaseOut, status_code=201)
def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    new_slug = slugify(case_data.title)
    case = case_service.get_case_by_slug(db, new_slug)

    if case is not None:
        raise HTTPException(status_code=400, detail="Case Already Exists")

    return case_service.create_case(db, case_data, current_user.id)


@router.patch("/{case_id}", response_model=CaseOut, status_code=200)
def update_case(
    case_id: int,
    case_data: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    case = case_service.get_case(db, case_id)

    if case is None:
        raise HTTPException(status_code=404, detail="Case Not Found")

    if case.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Case"
        )

    new_slug = slugify(case_data.title)
    case_by_slug = case_service.get_case_by_slug(db, new_slug)

    if case_by_slug is not None and case_by_slug.id != case_id:
        raise HTTPException(status_code=400, detail="Case Already Exists")

    return case_service.update_case(db, case_data, case_id)


@router.delete("/{case_id}", status_code=200)
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> bool:
    case = case_service.get_case(db, case_id)

    if case is None:
        raise HTTPException(status_code=404, detail="Case Not Found")

    if case.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Case"
        )

    return case_service.delete_case(db, case_id)
