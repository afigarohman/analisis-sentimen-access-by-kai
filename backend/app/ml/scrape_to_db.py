"""Scrape ulasan Google Play ke database."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from google_play_scraper import reviews as gp_reviews
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.review import Review

APP_ID = "com.kai.kaiticketing"


def _label_from_score(score: int) -> str:
    if score >= 4:
        return "positive"
    if score == 3:
        return "neutral"
    return "negative"


def _stable_review_id(r: dict) -> str:
    raw = r.get("reviewId") or r.get("review_id")
    if raw is not None and str(raw).strip():
        return str(raw).strip()
    at = r.get("at")
    at_s = at.isoformat() if hasattr(at, "isoformat") else str(at)
    base = f"{r.get('content', '')}|{r.get('userName', '')}|{at_s}"
    return "gp-" + hashlib.sha256(base.encode("utf-8", errors="ignore")).hexdigest()[:28]


def scrape_google_reviews_to_db(db: Session, target: int) -> dict[str, int]:
    if target < 1:
        return {"imported": 0, "skipped_duplicates": 0, "requested": target}

    imported = 0
    skipped = 0
    token = None
    now = datetime.now(timezone.utc)

    while imported < target:
        need = min(200, target - imported)
        result, token = gp_reviews(
            APP_ID,
            lang="id",
            country="id",
            count=need,
            continuation_token=token,
        )

        if not result:
            break

        for r in result:
            if imported >= target:
                break

            content = (r.get("content") or "").strip()
            if not content:
                continue

            score = int(r.get("score") or 0)
            if score < 1 or score > 5:
                score = 3

            rid = _stable_review_id({**r, "content": content})

            exists = db.scalar(select(Review.id).where(Review.review_id == rid))
            if exists is not None:
                skipped += 1
                continue

            created_at = r.get("at")
            if created_at is not None and getattr(created_at, "tzinfo", None) is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

            rev = Review(
                review_id=rid,
                user_name=r.get("userName"),
                content=content,
                score=score,
                sentiment_label=_label_from_score(score),
                app_version=None,
                created_at=created_at,
                scraped_at=now,
                ai_reply=None,
                status="pending",
            )
            db.add(rev)
            try:
                db.commit()
                imported += 1
            except IntegrityError:
                db.rollback()
                skipped += 1

        if not token:
            break

    return {
        "imported": imported,
        "skipped_duplicates": skipped,
        "requested": target,
    }
