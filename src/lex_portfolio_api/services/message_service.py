from sqlalchemy.orm import Session

from lex_portfolio_api.schemas.message import MessageCreate, MessageUpdate
from lex_portfolio_api.models.messages import Message

from datetime import datetime, timezone


def get_messages(db: Session, user_id: int) -> list[Message] | None:
    return (
        db.query(Message)
        .filter(Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .all()
    )


def get_message(db: Session, message_id: int) -> Message | None:
    return db.query(Message).filter(Message.id == message_id).first()


def create_message(
    message_schema: MessageCreate, db: Session, user_id: int
) -> dict[str, bool]:
    new_message = Message(
        name=message_schema.name,
        email=message_schema.email,
        phone=message_schema.phone,
        message=message_schema.message,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        read=False,
    )

    db.add(new_message)
    db.commit()

    return {"ok": True}


def update_message(
    message_schema: MessageUpdate, db: Session, message_id: int
) -> Message:
    message = get_message(db, message_id)
    message.read = message_schema.read

    db.commit()
    db.refresh(message)

    return message


def delete_message(db: Session, message_id: int) -> bool:
    message = get_message(db, message_id)

    if message is None:
        return False

    db.delete(message)
    db.commit()

    return True
