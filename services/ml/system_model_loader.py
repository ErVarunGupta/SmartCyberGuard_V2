import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_PATH = os.path.join(BASE_DIR, "models", "rf_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)


def predict_system(features):
    try:
        scaled = scaler.transform([features])
        pred = model.predict(scaled)[0]
        probs = model.predict_proba(scaled)[0]

        return pred, probs

    except Exception as e:
        print("ML Prediction Error:", e)
        return None, None