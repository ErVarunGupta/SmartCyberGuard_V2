import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# LOAD DATA
df = pd.read_csv("data/ids_dataset.csv")

X = df.drop("label", axis=1)
y = df["label"]

# SCALE (IMPORTANT)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# RANDOM FOREST
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_scaled, y)

joblib.dump(rf, "models/ids_rf_model.pkl")

# ISOLATION FOREST
iso = IsolationForest(contamination=0.1)
iso.fit(X_scaled)

joblib.dump(iso, "models/ids_iso_model.pkl")

# SAVE SCALER
joblib.dump(scaler, "models/ids_scaler.pkl")

print("✅ NEW IDS MODELS TRAINED")