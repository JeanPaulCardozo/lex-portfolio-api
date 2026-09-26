from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from lex_portfolio_api.database import get_db
from lex_portfolio_api.models.users import User
from lex_portfolio_api.core.security import decode_access_token
from lex_portfolio_api.services.users_service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    creadentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not valid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)

    if payload is None:
        return creadentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        return creadentials_exception

    user = get_user_by_id(db, user_id)
    if user is None:
        return creadentials_exception

    return user
