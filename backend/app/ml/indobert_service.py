import onnxruntime as ort
from transformers import BertTokenizer
import numpy as np
import os

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "indobert", "indobert_model.onnx")

tokenizer = BertTokenizer.from_pretrained("indobenchmark/indobert-base-p1")

session = ort.InferenceSession(MODEL_PATH)

labels = ["negative", "neutral", "positive"]

NEGATIVE_CUES = [
    "error", "gagal", "lemot", "bug",
    "crash",
    "jelek", "buruk",
    "tidak bisa", "ga bisa", "nggak bisa"
]

CONTRAST_WORDS = [
    "tapi", "namun", "tetapi",
    "walaupun", "meskipun",
    "cuma", "cuman"
]

def predict_sentiment(text: str):
    text_lower = text.lower()


    if any(c in text_lower for c in CONTRAST_WORDS):
        if any(n in text_lower for n in NEGATIVE_CUES):
            return {
                "label": "negative",
                "confidence": 0.75
            }

   
    inputs = tokenizer(
        text,
        return_tensors="np",
        truncation=True,
        padding="max_length",
        max_length=128
    )

    ort_inputs = {
        "input_ids": inputs["input_ids"].astype(np.int64),
        "attention_mask": inputs["attention_mask"].astype(np.int64),
    }

    if "token_type_ids" in inputs:
        ort_inputs["token_type_ids"] = inputs["token_type_ids"].astype(np.int64)

    outputs = session.run(None, ort_inputs)
    logits = outputs[0]

    # softmax manual
    exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)

    pred = int(np.argmax(probs))
    label = labels[pred]
    confidence = float(probs[0][pred])

    return {
        "label": label,
        "confidence": round(confidence, 4)
    }