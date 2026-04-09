import json
import time
import os

DATA_PATH = "data/ai_brain_dataset.jsonl"

os.makedirs("data", exist_ok=True)


def save_knowledge(user, context, response, intent):
    record = {
        "user": user,
        "context": context,
        "response": response,
        "intent": intent,
        "timestamp": time.time()
    }

    try:
        with open(DATA_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print("Knowledge save error:", e)