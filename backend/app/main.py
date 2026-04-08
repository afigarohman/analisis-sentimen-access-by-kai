from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.models.review import Review
from app.routers.reviews import router as reviews_router
from app.routers.dashboard import router as dashboard_router

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

app.include_router(reviews_router)

app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

@app.get("/")
def root():
    return {"message": "Backend FastAPI is running"}