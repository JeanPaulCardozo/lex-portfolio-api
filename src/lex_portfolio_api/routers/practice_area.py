from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from lex_portfolio_api.schemas.practice_area import (
    PracticeAreaOut,
    PracticeAreaCreate,
    PracticeAreaUpdate,
)
from lex_portfolio_api.database import get_db
from lex_portfolio_api.core.dependencies import get_current_user
from lex_portfolio_api.models.users import User
from lex_portfolio_api.services import practice_area_service
from lex_portfolio_api.core.slugify import slugify

router = APIRouter(prefix="/practice-areas", tags=["practice-areas"])


@router.get("/", response_model=list[PracticeAreaOut], status_code=200)
def get_all_practice_areas(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return practice_area_service.get_practice_areas(db, current_user.id)


@router.get("/{slug}", response_model=PracticeAreaOut, status_code=200)
def get_practice_area_by_slug(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    practice_area = practice_area_service.get_practice_area_by_slug(db, slug)

    if practice_area is None:
        raise HTTPException(status_code=404, detail="Practice Area Not Found")

    if practice_area.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Practice Area"
        )

    return practice_area


@router.post("/", response_model=PracticeAreaOut, status_code=201)
def create_practice_area(
    new_practice_area: PracticeAreaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    new_slug = slugify(new_practice_area.name)
    practice_area = practice_area_service.get_practice_area_by_slug(db, new_slug)

    if practice_area is not None:
        raise HTTPException(status_code=400, detail="Practice Area Already Exists")

    return practice_area_service.create_practice_area(
        db, new_practice_area, current_user.id
    )


@router.patch("/{practice_area_id}", response_model=PracticeAreaOut, status_code=200)
def update_practice_area(
    practice_area_id: int,
    update_practice_area: PracticeAreaUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    practice_area = practice_area_service.get_practice_area(db, practice_area_id)

    if practice_area is None:
        raise HTTPException(status_code=404, detail="Practice Area Not Found")

    if practice_area.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access this Practice Area"
        )

    new_slug = slugify(update_practice_area.name)
    slug_owner = practice_area_service.get_practice_area_by_slug(db, new_slug)

    if slug_owner is not None and slug_owner.id != practice_area_id:
        raise HTTPException(status_code=400, detail="Practice Area Already Exists")

    return practice_area_service.update_practice_area(
        db, update_practice_area, practice_area_id
    )


@router.delete("/{practice_area_id}", status_code=200)
def delete_practice_area(
    practice_area_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    practice_area = practice_area_service.get_practice_area(db, practice_area_id)

    if practice_area is None:
        raise HTTPException(status_code=404, detail="Practice Area Not Found")

    if practice_area.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access this Practice Area"
        )

    return practice_area_service.delete_practice_area(db, practice_area_id)
