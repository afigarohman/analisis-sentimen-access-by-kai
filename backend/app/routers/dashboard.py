from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.review import Review

router = APIRouter()


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db)) -> dict:
    total_reviews = db.scalar(select(func.count(Review.id))) or 0
    total_positive = (
        db.scalar(
            select(func.count(Review.id)).where(Review.score.in_([4, 5]))
        )
        or 0
    )
    total_neutral = (
        db.scalar(select(func.count(Review.id)).where(Review.score == 3)) or 0
    )
    total_negative = (
        db.scalar(
            select(func.count(Review.id)).where(Review.score.in_([1, 2]))
        )
        or 0
    )
    avg = db.scalar(select(func.avg(Review.score)))
    average_score = float(avg) if avg is not None else 0.0
    return {
        "total_reviews": total_reviews,
        "total_positive": total_positive,
        "total_neutral": total_neutral,
        "total_negative": total_negative,
        "average_score": average_score,
    }


@router.get("/sentiment-distribution")
def sentiment_distribution(db: Session = Depends(get_db)) -> list[dict]:
    stmt = (
        select(Review.score, func.count(Review.id))
        .group_by(Review.score)
        .order_by(Review.score)
    )
    rows = db.execute(stmt).all()
    return [{"score": int(score), "total": int(total)} for score, total in rows]


@router.get("/review-growth")
def review_growth(db: Session = Depends(get_db)) -> list[dict]:
    day = func.date(Review.created_at)
    stmt = (
        select(day.label("d"), func.count(Review.id))
        .group_by(day)
        .order_by(day)
    )
    rows = db.execute(stmt).all()
    out: list[dict] = []
    for d, total in rows:
        if d is None:
            continue
        out.append({"date": d.isoformat(), "total": int(total)})
    return out


@router.get("/sentiment-trend")
def sentiment_trend(db: Session = Depends(get_db)) -> list[dict]:
    day = func.date(Review.created_at)
    stmt = (
        select(day.label("d"), Review.score, func.count(Review.id))
        .group_by(day, Review.score)
        .order_by(day, Review.score)
    )
    rows = db.execute(stmt).all()
    out: list[dict] = []
    for d, score, total in rows:
        if d is None:
            continue
        out.append(
            {
                "date": d.isoformat(),
                "score": int(score),
                "total": int(total),
            }
        )
    return out
