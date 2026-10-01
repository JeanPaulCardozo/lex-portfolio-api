from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from lex_portfolio_api.database import get_db
from lex_portfolio_api.models.users import User
from lex_portfolio_api.core.security import decode_access_token
from lex_portfolio_api.services.users_service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def _resolve_user_from_token(token: str | None, db: Session) -> User | None:
    if token is None:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    return get_user_by_id(db, user_id)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:

    user = _resolve_user_from_token(token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)
) -> User | None:
    return _resolve_user_from_token(token, db)
