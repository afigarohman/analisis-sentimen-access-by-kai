from google_play_scraper import reviews
import pandas as pd
import time


APP_ID = "com.kai.kaiticketing"  


def label_sentiment(score):
    if score >= 4:
        return "positive"
    elif score == 3:
        return "neutral"
    else:
        return "negative"


def scrape_reviews(target=10000):
    all_reviews = []
    continuation_token = None

    print("🚀 Mulai scraping...")

    while len(all_reviews) < target:
        result, continuation_token = reviews(
            APP_ID,
            lang="id",
            country="id",
            count=200,
            continuation_token=continuation_token
        )

        for r in result:
            rating = r["score"]

            if rating <= 3:
                all_reviews.append({
                    "review": r["content"],
                    "rating": rating,
                    "label": "negative" if rating <= 2 else "neutral"
                })

        print(f"Collected: {len(all_reviews)} reviews")

        if not continuation_token:
            break

        time.sleep(1)  

    df = pd.DataFrame(all_reviews)

    df_clean = df[["review", "rating", "label"]]

    df_clean.to_csv("dataset_10k.csv", index=False)
    print("✅ Selesai! Data disimpan ke dataset_10k.csv")


if __name__ == "__main__":
    scrape_reviews(10000)