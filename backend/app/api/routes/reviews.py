from fastapi import APIRouter, Depends
from app.ml.indobert_service import predict_sentiment

router = APIRouter()

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

