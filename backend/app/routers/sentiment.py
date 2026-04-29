from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ml.sentiment_service import predict_sentiment

router = APIRouter()


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)


class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float | None = None


@router.post("/sentiment", response_model=SentimentResponse)
def sentiment(body: SentimentRequest) -> SentimentResponse:
    try:
        result = predict_sentiment(text=body.text, rating=body.rating)
        return SentimentResponse(**result)
    except RuntimeError as e:
        # model/vectorizer not found or failed to load
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment prediction failed: {e}")

