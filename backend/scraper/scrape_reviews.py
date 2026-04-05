print("FILE SCRAPER TERBACA")

from google_play_scraper import reviews, Sort
from app.core.database import SessionLocal
from app.models.review import Review

import json
import pandas as pd

APP_ID = "com.kai.kaiticketing"


def map_score(score):
    return {
        1: "Jelek Sekali",
        2: "Jelek",
        3: "Netral",
        4: "Baik",
        5: "Baik Sekali"
    }.get(score, "tidak diketahui")


def scrape_and_save_reviews(count=100):
    db = SessionLocal()
    data_clean = []

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

            # 🔥 CLEAN DATA (INI YANG KURANG TADI)
            clean_item = {
                "review_id": review_id,
                "user_name": item.get("userName"),
                "content": item.get("content"),
                "score": item.get("score"),
                "sentiment_label": map_score(item.get("score")),
                "app_version": item.get("appVersion"),
                "created_at": item.get("at")
            }

            data_clean.append(clean_item)

            # 🔥 SIMPAN KE DATABASE
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

        # save to json
        with open("reviews.json", "w", encoding="utf-8") as f:
            json.dump(data_clean, f, ensure_ascii=False, indent=4)

        # save to excel
        df = pd.DataFrame(data_clean)
        df.to_excel("reviews.xlsx", index=False)

        print("Data berhasil disimpan ke JSON & Excel")

    except Exception as e:
        db.rollback()
        print("ERROR:", e)

    finally:
        db.close()


if __name__ == "__main__":
    print("Scraper dijalankan...")
    scrape_and_save_reviews(100)