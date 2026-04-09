import json
import time
import threading
import os

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib

DATA_PATH = "data/ai_brain_dataset.jsonl"
MODEL_PATH = "models/intent_model.pkl"


def train_model():
    if not os.path.exists(DATA_PATH):
        return

    texts = []
    labels = []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                texts.append(data["user"])
                labels.append(data["intent"])
            except:
                continue

    if len(texts) < 20:
        return  # wait for more data

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)

    model = RandomForestClassifier()
    model.fit(X, labels)

    joblib.dump((model, vectorizer), MODEL_PATH)

    print("✅ Model auto-trained with", len(texts), "samples")


# =========================
# BACKGROUND TRAINER
# =========================
def auto_train_loop():
    while True:
        try:
            train_model()
        except Exception as e:
            print("Training error:", e)

        # ⏱ Train every 5 minutes
        time.sleep(300)


def start_auto_trainer():
    thread = threading.Thread(target=auto_train_loop, daemon=True)
    thread.start()