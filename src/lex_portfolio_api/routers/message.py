from fastapi import APIRouter, HTTPException, Depends, Request

from sqlalchemy.orm import Session

from lex_portfolio_api.schemas.message import MessageUpdate, MessageCreate, MessageOut
from lex_portfolio_api.models.users import User
from lex_portfolio_api.database import get_db
from lex_portfolio_api.core.dependencies import get_current_user
from lex_portfolio_api.core.emails import (
    send_notification_email,
    build_contact_email_html,
)
from lex_portfolio_api.services import message_service, profile_service

from lex_portfolio_api.core.limiter import limiter

router = APIRouter(tags=["message"])


@router.get("/messages", response_model=list[MessageOut], status_code=200)
def get_messages(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return message_service.get_messages(db, current_user.id)


@router.post("/contact", response_model=dict[str, bool], status_code=201)
@limiter.limit("5/minute")
def create_message(
    request: Request, message: MessageCreate, db: Session = Depends(get_db)
):
    user = db.query(User).first()
    result = message_service.create_message(message, db, user.id)

    profile = profile_service.get_profile(db)
    if profile is not None:
        try:
            send_notification_email(
                to=profile.notify_email or profile.email,
                subject=f"Nuevo mensaje de {message.name}",
                html=build_contact_email_html(
                    message.name, message.email, message.message, message.phone
                ),
            )
        except Exception:
            pass

    return result


@router.patch("/messages/{message_id}", response_model=MessageOut, status_code=200)
def update_message(
    message_id: int,
    message: MessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_message = message_service.get_message(db, message_id)

    if current_message is None:
        raise HTTPException(status_code=404, detail="Message Not Found")

    if current_message.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Message"
        )

    return message_service.update_message(message, db, message_id)


@router.delete("/messages/{message_id}", status_code=200)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = message_service.get_message(db, message_id)

    if message is None:
        raise HTTPException(status_code=404, detail="Message Not Found")

    if message.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Message"
        )

    return message_service.delete_message(db, message_id)
