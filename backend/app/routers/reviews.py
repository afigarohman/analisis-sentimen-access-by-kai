from collections.abc import Sequence

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.review import Review
from app.schemas.review import ReviewRead
from fastapi import APIRouter
from app.ml.indobert_service import predict_sentiment

router = APIRouter(tags=["reviews"])
router = APIRouter()


# =========================
# REQUEST BODY
# =========================
class ApproveReviewBody(BaseModel):
    ai_reply: str = Field(
        ..., min_length=1, description="Teks balasan AI yang disetujui"
    )


# =========================
# GET REVIEWS
# =========================
@router.get("/reviews", response_model=list[ReviewRead])
def list_reviews(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> Sequence[Review]:
    stmt = (
        select(Review)
        .order_by(Review.created_at.desc().nulls_last(), Review.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


# =========================
# APPROVE REVIEW
# =========================
@router.post("/reviews/{review_id}/approve")
def approve_review(
    review_id: int,
    body: ApproveReviewBody,
    db: Session = Depends(get_db),
):
    review = db.get(Review, review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review tidak ditemukan")

    review.ai_reply = body.ai_reply
    review.status = "approved"

    db.commit()
    db.refresh(review)

    return {
        "message": "Review approved",
        "id": review.id,
        "status": review.status,
        "ai_reply": review.ai_reply,
    }


# =========================
# REJECT REVIEW
# =========================
@router.post("/reviews/{review_id}/reject")
def reject_review(
    review_id: int,
    db: Session = Depends(get_db),
):
    review = db.get(Review, review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review tidak ditemukan")

    review.status = "rejected"

    db.commit()
    db.refresh(review)

    return {
        "message": "Review rejected",
        "id": review.id,
        "status": review.status,
    }

@router.post("/predict")
def predict(data: dict):
    text = data.get("text")

    if not text:
        return {"error": "text is required"}

    result = predict_sentiment(text)

    return {
        "text": text,
        "result": result
    }