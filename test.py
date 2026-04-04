import joblib

scaler = joblib.load("models/scaler.pkl")
print(scaler.n_features_in_)