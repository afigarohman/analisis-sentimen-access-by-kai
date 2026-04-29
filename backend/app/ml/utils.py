import re

import numpy as np
from scipy.sparse import csr_matrix, hstack


_NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]+", flags=re.IGNORECASE)
_WS_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """
    Basic cleaning for Indonesian review text:
    - lowercase
    - remove symbols/punctuations
    - normalize whitespace
    """
    t = (text or "").lower()
    t = _NON_ALNUM_RE.sub(" ", t)
    t = _WS_RE.sub(" ", t).strip()
    return t


def prepare_input(text: str, rating: int, vectorizer):
    """
    Combine TF-IDF(text) + rating numeric feature into a single sparse row.
    """
    cleaned = clean_text(text)
    X_text = vectorizer.transform([cleaned])

    try:
        r = float(rating)
    except Exception:
        r = 0.0

    X_rating = csr_matrix(np.array([[r]], dtype=np.float32))
    return hstack([X_text, X_rating], format="csr")

