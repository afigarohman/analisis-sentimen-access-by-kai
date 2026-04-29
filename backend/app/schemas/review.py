from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

# Star rating → fixed 5-class labels (thesis mapping)
SCORE_TO_KELAS = {
    1: "jelek sekali",
    2: "jelek",
    3: "netral",
    4: "baik",
    5: "baik sekali",
}


class ReviewRead(BaseModel):
    """Serialized review row for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    review_id: str | None
    user_name: str | None
    content: str
    score: int
    sentiment_label: str | None
    app_version: str | None
    created_at: datetime | None
    scraped_at: datetime | None = None
    ai_reply: str | None = None
    status: str | None = None

    @computed_field
    @property
    def kelas_skor(self) -> str:
        return SCORE_TO_KELAS.get(self.score, "tidak diketahui")
