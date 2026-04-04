from fastapi import FastAPI
from app.core.database import Base, engine
from app.models.review import Review

app = FastAPI(
    title="Access By KAI Sentiment Dashboard API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Backend FastAPI is running"}