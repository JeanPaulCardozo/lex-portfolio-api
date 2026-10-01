from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.orm import Session

from lex_portfolio_api.models.users import User
from lex_portfolio_api.schemas.testimonial import (
    TestimonialUpdateStatus,
    TestimonialUpdate,
    TestimonialCreate,
    TestimonialCreateByPublic,
    TestimonialOut,
    TestimonialPublicOut
)
from lex_portfolio_api.services import testimonial_service
from lex_portfolio_api.database import get_db
from lex_portfolio_api.core.dependencies import get_current_user, get_current_user_optional

router = APIRouter(prefix="/testimonials", tags=["testimonials"])

@router.get("/",response_model=None, status_code=200)
def get_testimonials(all: int = 0, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)):
    if all: 
        if current_user is None:
            raise HTTPException(status_code=403, detail="Not authenticated")
        testimonials = testimonial_service.get_all_testimonials(db, current_user.id)
        return [TestimonialOut.model_validate(testimonial) for testimonial in testimonials]

    testimonials = testimonial_service.get_testimonials(db)
    return [TestimonialPublicOut.model_validate(testimonial) for testimonial in testimonials]
    

@router.post("/submit", response_model=dict[str, bool], status_code=201)
def create_testimonial_by_public(
    testimonial_schema: TestimonialCreateByPublic, db: Session = Depends(get_db)
):
    user = db.query(User).first()

    return testimonial_service.create_testimonial_by_public(
        db, testimonial_schema, user.id
    )


@router.post("/", response_model=TestimonialOut, status_code=201)
def create_testimonial(
    testimonial_schema: TestimonialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return testimonial_service.create_testimonial(
        db, testimonial_schema, current_user.id
    )


@router.patch("/{testimonial_id}", response_model=TestimonialOut, status_code=200)
def update_testimonial(
    testimonial_id: int,
    testimonial_schema: TestimonialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    testimonial = testimonial_service.get_testimonial(db, testimonial_id)

    if testimonial is None:
        raise HTTPException(status_code=404, detail="Testimonial Not Found")

    if testimonial.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Testimonial"
        )

    return testimonial_service.update_testimonial(
        db, testimonial_schema, testimonial_id
    )


@router.patch(
    "/{testimonial_id}/status", response_model=TestimonialOut, status_code=200
)
def approval_testimonial(
    testimonial_id: int,
    testimonial_schema: TestimonialUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    testimonial = testimonial_service.get_testimonial(db, testimonial_id)

    if testimonial is None:
        raise HTTPException(status_code=404, detail="Testimonial Not Found")

    if testimonial.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Testimonial"
        )

    return testimonial_service.update_testimonial_status(
        db, testimonial_schema, testimonial_id
    )


@router.delete("/{testimonial_id}", status_code=200)
def delete_testimonial(
    testimonial_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    testimonial = testimonial_service.get_testimonial(db, testimonial_id)

    if testimonial is None:
        raise HTTPException(status_code=404, detail="Testimonial Not Found")

    if testimonial.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not Authorized To Access This Testimonial"
        )

    return testimonial_service.delete_testimonial(db, testimonial_id)
