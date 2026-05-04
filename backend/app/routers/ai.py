import os
import tempfile
import traceback
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ml.aspect_rules import ASPECTS, classify_aspect
from app.ml.feedback_rules import is_feedback, matched_feedback_keywords
from app.ml.data_export import export_reviews_for_training
from app.ml.indobert_service import predict_sentiment as predict_sentiment_ml
from app.ml.scrape_to_db import scrape_google_reviews_to_db
from app.ml.train import train
from app.models.review import Review

router = APIRouter()


class PredictBody(BaseModel):
    text: str = Field(..., description="Teks ulasan untuk dianalisis")


class GenerateReplyBody(BaseModel):
    content: str = Field(..., description="Isi ulasan pengguna")


class ScrapeBody(BaseModel):
    count: int = Field(default=50, ge=1, le=500)


class TrainBody(BaseModel):
    samples: int | None = Field(default=None, ge=1, le=100_000)
    max_features: int = Field(default=5000, ge=100, le=20000)


def extract_text(response) -> str:
    try:
        if hasattr(response, "text") and response.text:
            return response.text.strip()

        candidates = getattr(response, "candidates", [])
        if candidates:
            parts = candidates[0].content.parts
            return "".join([p.text for p in parts if hasattr(p, "text")]).strip()

    except Exception:
        pass

    return ""

def fallback_reply(content: str) -> str:
    """
    Fallback balasan sederhana jika provider LLM tidak tersedia.
    Maks 2 kalimat, gaya santai, tanpa template kaku.
    """
    text = (content or "").strip()
    t = text.lower()

    # Heuristik ringan berbasis kata kunci.
    bad = any(
        w in t
        for w in [
            "ribet",
            "lemot",
            "lama",
            "error",
            "bug",
            "gagal",
            "tidak bisa",
            "ga bisa",
            "nggak bisa",
            "kecewa",
            "parah",
            "tolong",
            "susah",
            "payah",
        ]
    )
    good = any(w in t for w in ["bagus", "mantap", "membantu", "keren", "enak", "cepat", "love"])

    if bad:
        return "Makasih sudah kasih tahu ya—maaf jadi nggak nyaman. Kami coba cek dan perbaiki secepatnya."
    if good:
        return "Makasih banyak ya, senang banget kalau ini membantu. Kalau ada saran biar makin bagus, kabarin juga."
    return "Makasih sudah kasih ulasan ya. Kalau boleh, detail kendalanya apa biar kami bisa bantu cek lebih cepat?"


# PREDICT SENTIMENT

@router.post("/predict")
def predict_sentiment_api(body: PredictBody):
    text = body.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Teks tidak boleh kosong")

    try:
        result = predict_sentiment_ml(text)

        return {
            "text": text,
            "label": result["label"],
            "confidence": result["confidence"],
            "aspect": result["aspect"],
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Prediksi gagal: {str(e)}"
        )



# SCRAPING

@router.post("/scrape")
def scrape_reviews(body: ScrapeBody, db: Session = Depends(get_db)):
    try:
        stats = scrape_google_reviews_to_db(db, body.count)
        return {"message": "Scraping selesai", **stats}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"Scraping gagal: {str(e)}"
        )


# TRAIN MODEL

@router.post("/train")
def train_model(body: TrainBody, db: Session = Depends(get_db)):
    try:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "training.csv"

            n = export_reviews_for_training(db, csv_path, body.samples)

            if n < 20:
                raise HTTPException(
                    status_code=400,
                    detail="Data training kurang (minimal 20 data)"
                )

            out_dir = Path(__file__).resolve().parent.parent / "ml" / "artifacts"

            result = train(csv_path, out_dir, max_features=body.max_features)

            return {
                "message": "Training selesai",
                "samples": n,
                **result
            }

    except HTTPException:
        raise

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Training gagal: {str(e)}"
        )



@router.post("/generate-reply")
def generate_reply(body: GenerateReplyBody):
    content = body.content.strip()

    if not content:
        raise HTTPException(status_code=400, detail="Content tidak boleh kosong")

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        # Biar fitur tetap jalan di environment tanpa API key.
        return {"reply": fallback_reply(content)}

    prompt = f"""
Kamu adalah admin manusia (bukan bot) dari aplikasi Access by KAI.

Balas ulasan ini secara natural seperti orang beneran ngetik.
Jangan pakai template, jangan formal kaku.

Aturan:
- Variasikan gaya bahasa tiap jawaban
- Sesuaikan dengan emosi user
- Fokus ke masalah utama
- Boleh santai
- Maksimal 2 kalimat

Ulasan:
{content}

Balasan:
"""

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        reply = extract_text(response)

        if not reply:
            raise Exception("Response kosong dari Gemini")

        return {"reply": reply}

    except Exception as e:
        traceback.print_exc()
        # Jika provider gagal (quota, network, dll), tetap berikan balasan fallback.
        return {"reply": fallback_reply(content)}

@router.get("/feedback")
def get_feedback(db: Session = Depends(get_db)):
    """
    Ulasan yang mengandung saran / permintaan perbaikan (rule-based keywords),
    bukan filter utama berdasarkan sentimen negatif.
    """
    stmt = select(Review)
    reviews = db.scalars(stmt).all()

    allowed_labels = {"positive", "neutral", "negative"}
    items: list[dict[str, object]] = []

    for r in reviews:
        raw = (r.content or "").strip()
        if not raw or not is_feedback(raw):
            continue

        db_sentiment = (getattr(r, "sentiment_label", None) or "").lower().strip()
        sentiment = db_sentiment if db_sentiment in allowed_labels else None
        if sentiment is None:
            sentiment = predict_sentiment_ml(raw).get("label") or "unknown"

        aspect = classify_aspect(raw)
        items.append(
            {
                "text": raw,
                "aspect": aspect,
                "sentiment": str(sentiment),
                "matched_keywords": matched_feedback_keywords(raw),
            }
        )

    total = len(items)
    limit = 200
    limited = items[:limit]

    return {
        "total": total,
        "items": limited,
        **({"truncated": True, "shown": limit} if total > limit else {}),
    }


@router.get("/insight")
def get_insight(db: Session = Depends(get_db)):
    # Load all reviews, then compute (sentiment/aspect) on-demand.
    # - Aspect: classify_aspect() at runtime (and also if DB has no aspect field)
    # - Sentiment: prefer Review.sentiment_label; fallback to model if missing
    stmt = select(Review)
    reviews = db.scalars(stmt).all()

    allowed_labels = {"positive", "neutral", "negative"}
    aspect_counter: dict[str, int] = {a: 0 for a in ASPECTS}
    negative_samples: list[dict[str, str]] = []

    for r in reviews:
        text = (r.content or "").strip()
        if not text:
            continue

        db_sentiment = (getattr(r, "sentiment_label", None) or "").lower().strip()
        sentiment = db_sentiment if db_sentiment in allowed_labels else None

        aspect = getattr(r, "aspect", None)
        if not aspect:
            aspect = classify_aspect(text)

        # If sentiment not present in DB, compute from model.
        if sentiment is None:
            pred = predict_sentiment_ml(text)
            sentiment = pred.get("label")
            # If we computed sentiment, we can reuse model aspect too.
            aspect = pred.get("aspect") or aspect

        if sentiment != "negative":
            continue

        aspect_counter[aspect] = aspect_counter.get(aspect, 0) + 1
        negative_samples.append({"text": text, "aspect": str(aspect)})

    total_negative = len(negative_samples)
    aspect_distribution = {
        aspect: int(count)
        for aspect, count in aspect_counter.items()
        if count > 0
    }

    top_issues = [
        {"aspect": a, "count": int(c)}
        for a, c in sorted(aspect_counter.items(), key=lambda x: x[1], reverse=True)
        if c > 0
    ]

    # Keep samples deterministic and bounded.
    samples = negative_samples[:10]

    return {
        "total_negative": total_negative,
        "aspect_distribution": aspect_distribution,
        "top_issues": top_issues,
        "samples": samples,
    }