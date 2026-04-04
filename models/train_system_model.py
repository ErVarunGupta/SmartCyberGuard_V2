import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

data = pd.DataFrame({
    "cpu": [20, 50, 90],
    "ram": [30, 60, 95],
    "disk": [40, 70, 90],
    "battery": [80, 50, 20],
    "process": [100, 200, 400],
    "cpu_trend": [20, 55, 95],
    "ram_trend": [30, 65, 90],
    "load": [30, 60, 95],
    "label": [0, 1, 2]  # normal, moderate, high
})

X = data.drop("label", axis=1)
y = data["label"]

model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, "models/system_model.pkl")