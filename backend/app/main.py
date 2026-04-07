from fastapi import FastAPI

from app.core.database import Base, engine
from app.models.review import Review
from app.routers.reviews import router as reviews_router
from app.routers.dashboard import router as dashboard_router

app = FastAPI(
    title="Access By KAI Sentiment Dashboard API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(reviews_router)

app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

@app.get("/")
def root():
    return {"message": "Backend FastAPI is running"}