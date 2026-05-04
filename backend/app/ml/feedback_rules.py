from __future__ import annotations

# Urutkan frasa multi-kata dulu agar matching tidak terpotong oleh substring pendek.
FEEDBACK_KEYWORDS: list[str] = [
    "lebih baik",
    "kedepannya",
    "sebaiknya",
    "seharusnya",
    "tolong",
    "harap",
    "mohon",
    "saran",
]


def is_feedback(text: str) -> bool:
    """True jika ulasan mengindikasikan saran / permintaan perbaikan."""
    t = (text or "").lower()
    return any(k in t for k in FEEDBACK_KEYWORDS)


def matched_feedback_keywords(text: str) -> list[str]:
    """Kata / frasa yang terdeteksi (untuk highlight di UI)."""
    t = (text or "").lower()
    matched: list[str] = []
    for k in FEEDBACK_KEYWORDS:
        if k in t:
            matched.append(k)
    return matched
