"""
Train IndoBERT sentiment classifier (Transformers).

Run:
  python -m app.ml.train_indobert

Output:
  app/ml/model/  (model + tokenizer)

Notes:
- Uses ONLY `review` (text) as input and `label` as target.
- Does NOT use `rating`.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

import evaluate
from datasets import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)


MODEL_NAME = "indobenchmark/indobert-base-p1"
MAX_LENGTH = 128
NUM_LABELS = 3
SEED = 42


@dataclass(frozen=True)
class TrainConfig:
    csv_path: Path
    out_dir: Path
    num_train_epochs: int = 5
    batch_size: int = 8
    max_features: int = 5000  # kept for compatibility; not used for IndoBERT


def _clean_text(s: str) -> str:
    s = str(s).lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _load_dataset(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    required = {"review", "label"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {sorted(missing)}")

    df = df[["review", "label"]].copy()
    df["review"] = df["review"].astype(str).map(_clean_text)
    df["label"] = df["label"].astype(str).str.strip().str.lower()

    # drop kosong + terlalu pendek (<10 chars)
    df = df.dropna(subset=["review", "label"])
    df = df[df["review"].str.len() >= 10].reset_index(drop=True)

    allowed = {"positive", "neutral", "negative"}
    df = df[df["label"].isin(allowed)].reset_index(drop=True)
    if df.empty:
        raise ValueError("Dataset is empty after cleaning.")

    return df


def _build_hf_datasets(df: pd.DataFrame, tokenizer) -> tuple[Dataset, Dataset, LabelEncoder]:
    le = LabelEncoder()
    y = le.fit_transform(df["label"].values)

    train_df, test_df = train_test_split(
        df.assign(labels=y),
        test_size=0.10,
        random_state=SEED,
        stratify=y,
    )

    train_ds = Dataset.from_pandas(train_df[["review", "labels"]], preserve_index=False)
    test_ds = Dataset.from_pandas(test_df[["review", "labels"]], preserve_index=False)

    def tokenize_fn(batch):
        return tokenizer(
            batch["review"],
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
        )

    train_ds = train_ds.map(tokenize_fn, batched=True, remove_columns=["review"])
    test_ds = test_ds.map(tokenize_fn, batched=True, remove_columns=["review"])

    return train_ds, test_ds, le


def train_indobert(cfg: TrainConfig) -> dict[str, object]:
    df = _load_dataset(cfg.csv_path)
    print("✅ Loaded rows:", len(df))
    print("📊 Label distribution:")
    print(df["label"].value_counts())

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_ds, test_ds, le = _build_hf_datasets(df, tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_LABELS,
    )

    accuracy_metric = evaluate.load("accuracy")
    f1_metric = evaluate.load("f1")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        acc = accuracy_metric.compute(predictions=preds, references=labels)["accuracy"]
        f1 = f1_metric.compute(
            predictions=preds, references=labels, average="macro"
        )["f1"]
        return {"accuracy": acc, "f1_macro": f1}

    # Save to app/ml/model/
    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    args = TrainingArguments(
        output_dir=str(cfg.out_dir),
        num_train_epochs=cfg.num_train_epochs,
        per_device_train_batch_size=cfg.batch_size,
        per_device_eval_batch_size=cfg.batch_size,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        save_total_limit=2,
        logging_strategy="steps",
        logging_steps=50,
        seed=SEED,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics,
    )

    trainer.train()
    metrics = trainer.evaluate()
    print("\n🎯 Final eval metrics:", metrics)

    # Persist model + tokenizer
    trainer.save_model(str(cfg.out_dir))
    tokenizer.save_pretrained(str(cfg.out_dir))

    # Optional: save label mapping for inference consistency
    mapping_path = cfg.out_dir / "label_classes.txt"
    with mapping_path.open("w", encoding="utf-8") as f:
        for c in le.classes_:
            f.write(f"{c}\n")

    return {
        "rows": int(len(df)),
        "out_dir": str(cfg.out_dir.resolve()),
        "metrics": metrics,
        "label_classes": list(map(str, le.classes_)),
    }


def main() -> None:
    ml_dir = Path(__file__).resolve().parent
    csv_path = ml_dir / "dataset_final.csv"
    out_dir = ml_dir / "model"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}. Expected backend/app/ml/dataset_final.csv"
        )

    # Reduce tokenizer parallelism warning noise (optional).
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    cfg = TrainConfig(csv_path=csv_path, out_dir=out_dir)
    result = train_indobert(cfg)
    print("\n✅ Saved to:", result["out_dir"])


if __name__ == "__main__":
    main()

