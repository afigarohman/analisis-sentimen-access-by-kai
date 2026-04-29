import os
import tempfile
import traceback
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ml.data_export import export_reviews_for_training
from app.ml.indobert_service import predict_sentiment as predict_sentiment_ml
from app.ml.scrape_to_db import scrape_google_reviews_to_db
from app.ml.train import train

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


# =========================
# 🔥 PREDICT SENTIMENT
# =========================
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
            "confidence": result["confidence"]
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Prediksi gagal: {str(e)}"
        )


# =========================
# 🔥 SCRAPING
# =========================
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


# =========================
# 🔥 TRAIN MODEL
# =========================
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


# =========================
# 🔥 GENERATE AI REPLY
# =========================
@router.post("/generate-reply")
def generate_reply(body: GenerateReplyBody):
    content = body.content.strip()

    if not content:
        raise HTTPException(status_code=400, detail="Content tidak boleh kosong")

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY belum diset")

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
        raise HTTPException(
            status_code=502,
            detail=f"Gagal generate AI: {str(e)}"
        )