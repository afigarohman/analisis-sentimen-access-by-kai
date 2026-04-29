from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(String, unique=True, nullable=True)
    user_name = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)
    sentiment_label = Column(String, nullable=True)
    app_version = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, nullable=True)
    ai_reply = Column(Text, nullable=True)
    status = Column(String, nullable=True)