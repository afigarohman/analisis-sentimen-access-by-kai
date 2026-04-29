from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from app.ml.utils import clean_text


# =========================
# LOAD DATASET
# =========================
def _load_dataset(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    required = {"review", "rating", "label"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {sorted(missing)}")

    df = df.copy()
    df["review"] = df["review"].astype(str).map(clean_text)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)
    df["label"] = df["label"].astype(str).str.strip().str.lower()

    allowed = {"positive", "neutral", "negative"}
    bad = sorted(set(df["label"]) - allowed)
    if bad:
        raise ValueError(f"Invalid labels found: {bad}")

    df = df[df["review"].str.len() > 0].reset_index(drop=True)

    if df.empty:
        raise ValueError("Dataset is empty after cleaning.")

    return df


# =========================
# TRAIN MODEL
# =========================
def train(csv_path: Path, out_dir: Path, max_features: int = 5000) -> dict[str, Any]:
    df = _load_dataset(csv_path)

    print("📊 Distribusi label:")
    print(df["label"].value_counts())

    # TF-IDF
    vectorizer = TfidfVectorizer(max_features=max_features)
    X_text = vectorizer.fit_transform(df["review"])

    # Tambah rating sebagai fitur
    X_rating = csr_matrix(df["rating"].values.reshape(-1, 1))
    X = hstack([X_text, X_rating])

    y = df["label"].values

    # Split
    use_stratify = len(set(y)) > 1 and len(df) > 50

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y if use_stratify else None,
    )

    # Model (FIXED)
    model = LogisticRegression(
        max_iter=2000,
        solver="lbfgs",
        class_weight="balanced"  # 🔥 penting
    )

    model.fit(X_train, y_train)

    # Evaluasi
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"\n🎯 Accuracy: {acc:.4f}")
    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, digits=4))

    # Save
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / "model_sentiment.pkl")
    joblib.dump(vectorizer, out_dir / "vectorizer.pkl")

    print("\n✅ Model saved!")

    return {
        "accuracy": float(acc),
        "samples": int(len(df)),
        "artifacts_dir": str(out_dir.resolve()),
    }


# =========================
# OPTIONAL LABEL GENERATOR
# =========================
def generate_label(text: str, rating: int) -> str:
    text = text.lower()

    if any(word in text for word in ["jelek", "error", "lemot", "gagal", "bug"]):
        return "negative"
    elif any(word in text for word in ["bagus", "mantap", "cepat", "mudah"]):
        return "positive"
    elif rating == 3:
        return "neutral"
    else:
        return "neutral"


# =========================
# MAIN
# =========================
def main() -> None:
    default_out = Path(__file__).resolve().parent / "artifacts"

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", default=str(default_out))
    parser.add_argument("--max-features", type=int, default=5000)

    args = parser.parse_args()

    train(Path(args.csv), Path(args.out), max_features=args.max_features)


if __name__ == "__main__":
    main()