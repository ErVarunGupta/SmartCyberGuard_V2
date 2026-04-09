import json
import os
import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = "data/ai_brain_dataset.jsonl"

# 🔥 Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

corpus = []
responses = []
embeddings = None


# =========================
# LOAD DATA
# =========================
def load_data():
    global corpus, responses, embeddings

    if not os.path.exists(DATA_PATH):
        return

    texts = []
    replies = []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                texts.append(data["user"])
                replies.append(data["response"])
            except:
                continue

    if len(texts) < 10:
        print("Not enough data for response model")
        return

    corpus = texts
    responses = replies

    # 🔥 Generate embeddings
    embeddings = model.encode(corpus, convert_to_numpy=True)

    print(f"✅ Semantic model loaded with {len(corpus)} samples")


# =========================
# GET BEST RESPONSE
# =========================
def get_similar_response(user_query):
    global embeddings

    if not corpus or embeddings is None:
        return None, 0.0

    try:
        query_embedding = model.encode([user_query], convert_to_numpy=True)

        similarities = cosine_similarity(query_embedding, embeddings)[0]

        best_idx = np.argmax(similarities)
        score = similarities[best_idx]

        return responses[best_idx], score

    except Exception as e:
        print("Semantic error:", e)
        return None, 0.0