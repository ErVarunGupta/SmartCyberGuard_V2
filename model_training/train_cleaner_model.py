import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
df = pd.read_csv("data/cleaner_dataset.csv")

X = df[["size", "age_days", "is_temp", "is_download", "ext_len"]]
y = df["label"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Accuracy
acc = model.score(X_test, y_test)
print(f"Accuracy: {acc}")

# Save
joblib.dump(model, "models/cleaner_model.pkl")

print("✅ Model saved")