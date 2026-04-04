import psutil
import time
import joblib
import os
import pandas as pd

# =========================
# PATH SETUP
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "models", "rf_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

FEATURE_COLUMNS = [
    "cpu_usage",
    "ram_usage",
    "disk_usage",
    "disk_read",
    "disk_write",
    "battery_percent",
    "process_count",
    "heavy_process_count"
]

# =========================
# CACHE
# =========================
_last_data = None
_last_time = 0
CACHE_INTERVAL = 2  # seconds

# =========================
# PROCESS CACHE (IMPORTANT)
# =========================
_process_cache = []
_process_time = 0


def get_top_processes():
    global _process_cache, _process_time

    # 🔥 cache for 3 sec
    if time.time() - _process_time < 3:
        return _process_cache

    processes = []

    for p in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
        try:
            cpu = p.info['cpu_percent']
            if cpu is None:
                continue

            processes.append({
                "name": str(p.info['name']),
                "cpu": float(round(cpu, 1)),
                "ram": float(round(p.info['memory_percent'], 1))
            })
        except:
            continue

    processes = sorted(processes, key=lambda x: x['cpu'], reverse=True)[:5]

    _process_cache = processes
    _process_time = time.time()

    return processes


# =========================
# FAST FEATURE EXTRACTION
# =========================
def extract_features_fast(cpu):
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    disk_io = psutil.disk_io_counters()
    disk_read = disk_io.read_bytes / (1024 * 1024)
    disk_write = disk_io.write_bytes / (1024 * 1024)

    battery = psutil.sensors_battery()
    battery_percent = battery.percent if battery else 100

    process_count = len(psutil.pids())

    # ⚡ Avoid heavy loop here
    heavy_process_count = 0

    return [
        cpu,
        ram,
        disk,
        disk_read,
        disk_write,
        battery_percent,
        process_count,
        heavy_process_count
    ]


# =========================
# MAIN FUNCTION
# =========================
def get_system_metrics():
    global _last_data, _last_time

    # 🔥 RETURN CACHE
    if _last_data and (time.time() - _last_time < CACHE_INTERVAL):
        return _last_data

    start = time.time()

    try:
        # =========================
        # ⚡ NON-BLOCKING CPU
        # =========================
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        battery = psutil.sensors_battery()
        battery_percent = battery.percent if battery else 100

        # =========================
        # FEATURES
        # =========================
        features = extract_features_fast(cpu)

        X_df = pd.DataFrame([features], columns=FEATURE_COLUMNS)
        X_scaled = scaler.transform(X_df)

        pred = int(model.predict(X_scaled)[0])
        probs = model.predict_proba(X_scaled)[0].tolist()

        # =========================
        # STATE
        # =========================
        if pred == 0:
            state = "Normal"
        elif pred == 1:
            state = "Moderate"
        else:
            state = "High Load"

        # =========================
        # HEALTH SCORE
        # =========================
        normal_p, moderate_p, high_p = probs
        health = (normal_p * 100) - (high_p * 50)
        health = round(max(0, min(100, health)), 2)

    except Exception as e:
        print("ML ERROR:", e)

        # fallback
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        battery_percent = 100

        state = "Normal"
        health = 75
        pred = 0
        probs = []

    # =========================
    # RECOMMENDATIONS
    # =========================
    recommendation = []

    if probs and len(probs) > 2 and probs[2] > 0.5:
        recommendation.append("Close heavy applications")

    if cpu > 80:
        recommendation.append("Reduce CPU usage")

    if ram > 80:
        recommendation.append("Free RAM")

    if not recommendation:
        recommendation.append("System is stable")

    # =========================
    # FINAL RESPONSE
    # =========================
    data = {
        "cpu": float(cpu),
        "ram": float(ram),
        "disk": float(disk),
        "battery": int(battery_percent),

        "state": state,
        "health_score": float(health),

        "prediction": int(pred),
        "probabilities": probs,

        "recommendation": recommendation,
        "top_processes": get_top_processes()
    }

    _last_data = data
    _last_time = time.time()

    print("⚡ API Response Time:", round(time.time() - start, 2), "sec")

    return data