from collections.abc import Sequence

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.review import Review
from app.schemas.review import ReviewRead

router = APIRouter(tags=["reviews"])


@router.get("/reviews", response_model=list[ReviewRead])
def list_reviews(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of rows to return"
    ),
) -> Sequence[Review]:
    stmt = (
        select(Review)
        .order_by(Review.created_at.desc().nulls_last(), Review.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())
