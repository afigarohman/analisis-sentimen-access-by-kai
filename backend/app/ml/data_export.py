"""Export ulasan dari DB ke CSV format training (review, rating, label)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.review import Review


def score_to_label(score: int) -> str:
    if score >= 4:
        return "positive"
    if score == 3:
        return "neutral"
    return "negative"


def export_reviews_for_training(db: Session, path: Path, limit: int | None) -> int:
    stmt = select(Review).where(Review.content.isnot(None))
    stmt = stmt.order_by(Review.id.desc())
    if limit is not None and limit > 0:
        stmt = stmt.limit(limit)

    rows = list(db.scalars(stmt).all())
    data: list[dict[str, object]] = []
    for r in rows:
        text = (r.content or "").strip()
        if not text:
            continue
        rating = int(r.score)
        data.append(
            {
                "review": text,
                "rating": rating,
                "label": score_to_label(rating),
            }
        )

    if not data:
        return 0

    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(data).to_csv(path, index=False)
    return len(data)
