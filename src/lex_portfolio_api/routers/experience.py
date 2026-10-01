from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from lex_portfolio_api.schemas.experience import (
    ExperienceOut,
    ExperienceCreate,
    ExperienceUpdate,
)
from lex_portfolio_api.services import experience_service
from lex_portfolio_api.database import get_db
from lex_portfolio_api.core.dependencies import get_current_user
from lex_portfolio_api.models.users import User

router = APIRouter(prefix="/experience", tags=["experience"])


@router.get("/", response_model=list[ExperienceOut], status_code=200)
def get_experiences(db: Session = Depends(get_db)):
    return experience_service.get_experiences(db)


@router.post("/", response_model=ExperienceOut, status_code=201)
def create_experience(
    experience: ExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return experience_service.create_experience(db, experience, current_user.id)


@router.patch("/{experience_id}", response_model=ExperienceOut, status_code=200)
def update_experience(
    experience_id: int,
    experience: ExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    current_experience = experience_service.get_experience(db, experience_id)

    if current_experience is None:
        raise HTTPException(status_code=404, detail="Experience Not Found")

    if current_experience.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Experience"
        )

    return experience_service.update_experience(db, experience, experience_id)


@router.delete("/{experience_id}", status_code=200)
def delete_experience(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    current_experience = experience_service.get_experience(db, experience_id)

    if current_experience is None:
        raise HTTPException(status_code=404, detail="Experience Not Found")

    if current_experience.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Experience"
        )

    return experience_service.delete_experience(db, experience_id)
