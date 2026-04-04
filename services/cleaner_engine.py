import os
import time
import joblib
import numpy as np

import time
SCAN_TIMEOUT = 25   # seconds


MODEL_PATH = "models/cleaner_model.pkl"

try:
    model = joblib.load(MODEL_PATH)
except:
    model = None

# =========================
# CONFIG (SAFE PATHS ONLY)
# =========================
SCAN_PATHS = [
    os.path.expanduser("~\\AppData\\Local\\Temp"),
    os.path.expanduser("~\\Downloads")
]

# 🚫 Never touch system folders
SYSTEM_PATHS = [
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)"
]

SAFE_EXT = (".tmp", ".log", ".cache", ".bak")
IMPORTANT_EXT = (".exe", ".dll", ".sys", ".ini")


# =========================
# SAFETY CHECK
# =========================
def is_system_file(path):
    return any(path.startswith(p) for p in SYSTEM_PATHS)


# =========================
# FEATURE EXTRACTION
# =========================
def extract_features(path):
    try:
        stat = os.stat(path)

        size_mb = stat.st_size / (1024 * 1024)
        modified = stat.st_mtime
        accessed = stat.st_atime

        now = time.time()

        return {
            "path": path,
            "size": round(size_mb, 2),
            "age_days": int((now - modified) / 86400),
            "last_access_days": int((now - accessed) / 86400),
            "extension": os.path.splitext(path)[1].lower(),
            "is_temp": "temp" in path.lower(),
            "is_download": "download" in path.lower()
        }

    except Exception:
        return None


# =========================
# CLASSIFICATION ENGINE
# =========================
def classify_file(file):
    path = file["path"]
    ext = file["extension"]
    age = file["age_days"]
    size = file["size"]

    # 🚫 SYSTEM PROTECTION
    if is_system_file(path) or ext in IMPORTANT_EXT:
        return "IMPORTANT"

    # 🟢 SAFE TEMP FILES
    if ext in SAFE_EXT and age > 3:
        return "SAFE"

    # 🟡 OLD & LARGE FILES
    if age > 60 and size > 50:
        return "JUNK"

    # 🔵 RECENT FILES
    if age < 7:
        return "IMPORTANT"

    return "REVIEW"


# =========================
# MAIN SCAN FUNCTION
# =========================
import concurrent.futures

MAX_WORKERS = 6   # optimal for laptop
MAX_FILES = 1000


def scan_folder(base):
    results = []
    total_size = 0

   

    for root, _, files in os.walk(base):
        if len(results) >= MAX_FILES:
            break
        for f in files:
            if len(results) > MAX_FILES:
                break
            path = os.path.join(root, f)

            data = extract_features(path)
            if data["size"] < 0.001:   # skip useless tiny files
                continue
            if not data:
                continue


            rule_category = classify_file(data)

            ai_pred, confidence = ai_predict(data)

            mapping = ["SAFE", "REVIEW", "IMPORTANT"]

            if ai_pred is not None and confidence > 0.75:
                category = mapping[ai_pred]
            else:
                category = rule_category

            explanation = explain_file(data, category)

            data["category"] = category
            data["reason"] = explanation["reason"]
            data["confidence"] = explanation["confidence"]
            data["priority"] = explanation["priority"]

            if category in ["SAFE", "JUNK"]:
                total_size += data["size"]

            results.append(data)

    return results, total_size


def scan_system():
    all_results = []
    total_size = 0
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []

        for path in SCAN_PATHS:
            if os.path.exists(path):
                futures.append(executor.submit(scan_folder, path))

            if time.time() - start_time > SCAN_TIMEOUT:
                return all_results, total_size

        for future in concurrent.futures.as_completed(futures):
            try:
                results, size = future.result()
                all_results.extend(results)
                total_size += size
            except Exception:
                continue

    return all_results, total_size



def explain_file(file, category):

    age = file["age_days"]
    size = file["size"]
    ext = file["extension"]

    # =========================
    # SAFE
    # =========================
    if category == "SAFE":
        return {
            "reason": "Temporary/cache file not used recently",
            "confidence": 90,
            "priority": "HIGH"
        }

    # =========================
    # JUNK
    # =========================
    elif category == "JUNK":
        return {
            "reason": f"Old file ({age} days) and large size ({size} MB)",
            "confidence": 80,
            "priority": "MEDIUM"
        }

    # =========================
    # REVIEW
    # =========================
    elif category == "REVIEW":
        return {
            "reason": "May be important, review before deleting",
            "confidence": 60,
            "priority": "LOW"
        }

    # =========================
    # IMPORTANT
    # =========================
    return {
        "reason": "System or recent file, do not delete",
        "confidence": 95,
        "priority": "CRITICAL"
    }


import pandas as pd

def ai_predict(file):
    if model is None:
        return None, 0

    df = pd.DataFrame([{
        "size": file["size"],
        "age_days": file["age_days"],
        "is_temp": int(file["is_temp"]),
        "is_download": int(file["is_download"]),
        "ext_len": len(file["extension"])
    }])

    pred = model.predict(df)[0]
    prob = max(model.predict_proba(df)[0])

    return pred, prob