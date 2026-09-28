from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from lex_portfolio_api.schemas.profile import ProfileOut, CreateProfile, UpdateProfile
from lex_portfolio_api.database import get_db
from lex_portfolio_api.models.profile import User
from lex_portfolio_api.core.dependencies import get_current_user
from lex_portfolio_api.services import profile_service

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=ProfileOut, status_code=200)
def get_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    profile_info = profile_service.get_profile(db, current_user.id)

    if profile_info is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile_info


@router.patch("/", response_model=ProfileOut, status_code=200)
def update_profile(
    profile_info: UpdateProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return profile_service.update_profile(db, profile_info, current_user.id)
