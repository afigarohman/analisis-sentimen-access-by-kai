from google_play_scraper import reviews, Sort
import pandas as pd
import time

APP_ID = "com.kai.kaiticketing"  
TARGET = 100000

all_reviews = []
continuation_token = None

print("Mulai scraping...")

while len(all_reviews) < TARGET:
    try:
        result, continuation_token = reviews(
            APP_ID,
            lang="id",
            country="id",
            sort=Sort.NEWEST,
            count=200,
            continuation_token=continuation_token
        )

        if not result:
            break

        for r in result:
            all_reviews.append({
                "review": r["content"],
                "rating": r["score"]
            })

        print(f"Collected: {len(all_reviews)}")

        time.sleep(1)

    except Exception as e:
        print("Error:", e)
        break

df = pd.DataFrame(all_reviews)

df.drop_duplicates(subset=["review"], inplace=True)

print("Total setelah deduplicate:", len(df))

df.to_csv("raw_100k.csv", index=False)
print("Saved ke raw_100k.csv")