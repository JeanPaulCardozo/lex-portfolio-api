from sqlalchemy.orm import Session

from lex_portfolio_api.models.publication import Publication
from lex_portfolio_api.schemas.publication import PublicationCreate, PublicationUpdate


def get_publications(db: Session) -> list[Publication] | None:
    return db.query(Publication).order_by(Publication.date.desc()).all()


def get_publication(db: Session, publication_id: int) -> Publication | None:
    return db.query(Publication).filter(Publication.id == publication_id).first()


def create_publication(
    db: Session, publication_schema: PublicationCreate, user_id: int
) -> Publication:
    new_publication = Publication(
        title=publication_schema.title,
        kind=publication_schema.kind,
        venue=publication_schema.venue,
        date=publication_schema.date,
        url=publication_schema.url,
        summary=publication_schema.summary,
        user_id=user_id,
    )

    db.add(new_publication)
    db.commit()
    db.refresh(new_publication)

    return new_publication


def update_publication(
    db: Session, publication_schema: PublicationUpdate, publication_id: int
) -> Publication:
    publication = get_publication(db, publication_id)
    new_data = publication_schema.model_dump(exclude_unset=True)

    for label, value in new_data.items():
        setattr(publication, label, value)

    db.commit()
    db.refresh(publication)

    return publication


def delete_publication(db: Session, publication_id: int) -> bool:
    publication = get_publication(db, publication_id)

    if publication is None:
        return False

    db.delete(publication)
    db.commit()

    return True
