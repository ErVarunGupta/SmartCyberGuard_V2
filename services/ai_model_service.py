import joblib

try:
    model, vectorizer = joblib.load("models/intent_model.pkl")
except:
    model = None
    vectorizer = None


def predict_intent_with_confidence(text):
    if model is None or vectorizer is None:
        return "general", 0.0

    try:
        X = vectorizer.transform([text])
        probs = model.predict_proba(X)[0]
        max_prob = max(probs)
        label = model.classes_[probs.argmax()]

        return label, max_prob
    except:
        return "general", 0.0