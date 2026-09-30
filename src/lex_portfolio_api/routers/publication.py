from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.orm import Session

from lex_portfolio_api.models.users import User
from lex_portfolio_api.core.dependencies import get_current_user
from lex_portfolio_api.schemas.publication import (
    PublicationUpdate,
    PublicationCreate,
    PublicationOut,
)
from lex_portfolio_api.services import publication_service
from lex_portfolio_api.database import get_db

router = APIRouter(prefix="/publications", tags=["publications"])


@router.get("/", response_model=list[PublicationOut], status_code=200)
def get_publications(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return publication_service.get_publications(db, current_user.id)


@router.post("/", response_model=PublicationOut, status_code=201)
def create_publication(
    publication: PublicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return publication_service.create_publication(db, publication, current_user.id)


@router.patch("/{publication_id}", response_model=PublicationOut, status_code=200)
def update_publication(
    publication_id: int,
    publication: PublicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_publication = publication_service.get_publication(db, publication_id)

    if current_publication is None:
        raise HTTPException(status_code=404, detail="Publication Not Found")

    if current_publication.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Publication"
        )

    return publication_service.update_publication(db, publication, publication_id)


@router.delete("/{publication_id}", status_code=200)
def delete_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_publication = publication_service.get_publication(db, publication_id)

    if current_publication is None:
        raise HTTPException(status_code=404, detail="Publication Not Found")

    if current_publication.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Publication"
        )

    return publication_service.delete_publication(db, publication_id)
