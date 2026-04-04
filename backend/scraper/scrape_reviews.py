print("FILE SCRAPER TERBACA")

from google_play_scraper import reviews, Sort
from app.core.database import SessionLocal
from app.models.review import Review

APP_ID = "com.kai.kaiticketing"


def scrape_and_save_reviews(count=100):
    db = SessionLocal()

    try:
        print("Mulai scraping review...")
        result, _ = reviews(
            APP_ID,
            lang="id",
            country="id",
            sort=Sort.NEWEST,
            count=count
        )

        print(f"Jumlah review hasil scraping: {len(result)}")

        inserted = 0

        for item in result:
            review_id = item.get("reviewId")

            existing = db.query(Review).filter(Review.review_id == review_id).first()
            if existing:
                continue

            new_review = Review(
                review_id=review_id,
                user_name=item.get("userName"),
                content=item.get("content"),
                score=item.get("score"),
                sentiment_label=None,
                app_version=item.get("appVersion"),
                created_at=item.get("at")
            )

            db.add(new_review)
            inserted += 1

        db.commit()
        print(f"Berhasil menyimpan {inserted} review")

    except Exception as e:
        db.rollback()
        print("ERROR:", e)

    finally:
        db.close()


if __name__ == "__main__":
    print("Scraper dijalankan...")
    scrape_and_save_reviews(100)