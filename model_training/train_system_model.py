import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "system_data_labeled.csv")

df = pd.read_csv(DATA_FILE)

FEATURES = [
    "cpu_usage",
    "ram_usage",
    "disk_usage",
    "disk_read",
    "disk_write",
    "battery_percent",
    "process_count",
    "heavy_process_count"
]

X = df[FEATURES]
y = df["label"]

# ✅ SCALER
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# MODEL
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# SAVE BOTH
joblib.dump(model, os.path.join(BASE_DIR, "models", "rf_model.pkl"))
joblib.dump(scaler, os.path.join(BASE_DIR, "models", "scaler.pkl"))

print("✅ Model + Scaler saved correctly")