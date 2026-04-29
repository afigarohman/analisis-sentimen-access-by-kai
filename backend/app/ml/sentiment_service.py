from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from app.ml.utils import prepare_input


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "model_sentiment.pkl"
VECTORIZER_PATH = ARTIFACT_DIR / "vectorizer.pkl"


_MODEL = None
_VECTORIZER = None
_LOAD_ERROR: str | None = None


def _load_artifacts_once() -> None:
    global _MODEL, _VECTORIZER, _LOAD_ERROR
    if _MODEL is not None and _VECTORIZER is not None:
        return
    if _LOAD_ERROR is not None:
        return

    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        if not VECTORIZER_PATH.exists():
            raise FileNotFoundError(f"Vectorizer not found at {VECTORIZER_PATH}")

        _MODEL = joblib.load(MODEL_PATH)
        _VECTORIZER = joblib.load(VECTORIZER_PATH)
    except Exception as e:
        _LOAD_ERROR = str(e)


_load_artifacts_once()


def predict_sentiment(text: str, rating: int) -> dict[str, Any]:
    """
    Predict sentiment label from review text + rating.
    Loads artifacts once (module-level) and reuses them.
    """
    _load_artifacts_once()
    if _LOAD_ERROR is not None:
        raise RuntimeError(
            f"Sentiment model artifacts not available. Train first. Detail: {_LOAD_ERROR}"
        )
    assert _MODEL is not None and _VECTORIZER is not None

    X = prepare_input(text=text, rating=rating, vectorizer=_VECTORIZER)
    pred = _MODEL.predict(X)[0]

    confidence = None
    if hasattr(_MODEL, "predict_proba"):
        proba = _MODEL.predict_proba(X)[0]
        confidence = float(proba.max())

    out: dict[str, Any] = {"sentiment": str(pred)}
    if confidence is not None:
        out["confidence"] = confidence
    return out

