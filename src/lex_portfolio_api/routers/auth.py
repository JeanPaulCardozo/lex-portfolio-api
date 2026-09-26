from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from lex_portfolio_api.database import get_db
from lex_portfolio_api.schemas.users import UserOut, UserCreate, Token
from lex_portfolio_api.services import users_service
from lex_portfolio_api.services.users_service import (
    get_user_by_email,
    authenticate_user,
)
from lex_portfolio_api.core.security import create_access_token
from lex_portfolio_api.core.dependencies import get_current_user
from lex_portfolio_api.models.users import User

from fastapi.security import OAuth2PasswordRequestForm

from lex_portfolio_api.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    exist_user = get_user_by_email(db, user.email)

    if exist_user is not None:
        raise HTTPException(status_code=400, detail="User Already Registered")

    return users_service.create_user(db, user)


@router.post("/login", response_model=Token, status_code=200)
@limiter.limit("5/minute")
def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = authenticate_user(db, form_data.username, form_data.password)

    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token)


@router.get("/me", response_model=UserOut, status_code=200)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
