import os
import time
import pandas as pd

SCAN_PATHS = [
    os.path.expanduser("~\\Downloads"),
    os.path.expanduser("~\\Desktop"),
    os.path.expanduser("~\\AppData\\Local\\Temp")
]


def extract_features(path):
    try:
        stat = os.stat(path)

        size = stat.st_size / (1024 * 1024)
        modified = stat.st_mtime

        now = time.time()

        age_days = int((now - modified) / 86400)

        ext = os.path.splitext(path)[1].lower()

        return {
            "path": path,
            "size": size,
            "age_days": age_days,
            "is_temp": int("temp" in path.lower()),
            "is_download": int("download" in path.lower()),
            "ext_len": len(ext)
        }

    except:
        return None


def auto_label(file):
    # Initial labeling logic (semi-AI)
    if file["is_temp"] == 1 and file["age_days"] > 3:
        return 0  # SAFE

    if file["age_days"] > 60 and file["size"] > 50:
        return 1  # REVIEW

    return 2  # IMPORTANT


def generate_dataset(limit=5000):
    data = []

    for base in SCAN_PATHS:
        for root, _, files in os.walk(base):
            for f in files:
                path = os.path.join(root, f)

                features = extract_features(path)
                if not features:
                    continue

                label = auto_label(features)

                features["label"] = label
                data.append(features)

                if len(data) >= limit:
                    break

    df = pd.DataFrame(data)
    df.to_csv("data/cleaner_dataset.csv", index=False)

    print("✅ Dataset saved: cleaner_dataset.csv")


if __name__ == "__main__":
    generate_dataset()