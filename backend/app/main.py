from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import Base, engine
from app.models.review import Review

from app.routers.reviews import router as reviews_router
from app.routers.dashboard import router as dashboard_router
from app.routers.ai import router as ai_router


def _ensure_review_columns() -> None:
    """Tambah kolom baru pada tabel reviews jika belum ada (PostgreSQL)."""
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE reviews ADD COLUMN IF NOT EXISTS scraped_at TIMESTAMP"
                )
            )
    except Exception:
        pass

app = FastAPI(
    title="Access By KAI Sentiment Dashboard API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
_ensure_review_columns()

app.include_router(reviews_router)
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])

@app.get("/")
def root():
    return {"message": "Backend FastAPI is running"}