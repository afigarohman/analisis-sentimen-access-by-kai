import pandas as pd

df = pd.read_csv("raw_100k.csv")

df = df.dropna()
df = df[df["review"].str.len() > 5]

df["label"] = df["rating"].apply(
    lambda x: "positive" if x >= 4 else ("neutral" if x == 3 else "negative")
)

df_pos = df[df["label"] == "positive"]
df_neu = df[df["label"] == "neutral"]
df_neg = df[df["label"] == "negative"]

min_count = min(len(df_pos), len(df_neu), len(df_neg))

df_pos = df_pos.sample(min_count, random_state=42)
df_neu = df_neu.sample(min_count, random_state=42)
df_neg = df_neg.sample(min_count, random_state=42)

df_final = pd.concat([df_pos, df_neu, df_neg])

df_final = df_final.sample(frac=1).reset_index(drop=True)

print(df_final["label"].value_counts())

df_final.to_csv("dataset_final.csv", index=False)
print("✅ Saved ke dataset_final.csv")