import sys
import os
import time
import threading
import pandas as pd
import joblib

# ==============================
# PATH FIX (VERY IMPORTANT)
# ==============================
if hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, BASE_DIR)

# ==============================
# SAFE IMPORTS
# ==============================
from features.monitoring.monitor import collect_system_metrics
from features.ai_assistant.predictor import predict_system_state
from features.anomaly_detection.network_sniffer import start_sniffing
from features.ai_assistant.ai_brain import analyze
from core.logger.logger import log_alert
from core.data_logger import log_system_data

# ==============================
# RESOURCE PATH
# ==============================
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(BASE_DIR, relative_path)

# ==============================
# LOAD ML MODEL
# ==============================
model = None
try:
    model_path = resource_path("models/model.pkl")
    model = joblib.load(model_path)

    log_alert(
        alert_type="MODEL_LOADED",
        source="AGENT",
        extra_info="ML model loaded"
    )
except Exception as e:
    log_alert(
        alert_type="MODEL_FALLBACK",
        source="AGENT",
        extra_info=str(e)
    )

# ==============================
# START IDS THREAD
# ==============================
def start_ids():
    try:
        start_sniffing()
    except Exception as e:
        log_alert(
            alert_type="IDS_ERROR",
            source="AGENT",
            extra_info=str(e)
        )

ids_thread = threading.Thread(target=start_ids, daemon=True)
ids_thread.start()

log_alert(
    alert_type="IDS_STARTED",
    source="AGENT",
    extra_info="IDS running"
)

# ==============================
# MAIN LOOP
# ==============================
print("🚀 SmartCyberGuard Background Service Started")

while True:
    try:
        # 1️⃣ Collect metrics
        metrics = collect_system_metrics()

        # 2️⃣ Log data safely
        try:
            log_system_data()
        except:
            pass

        # 3️⃣ Prepare ML features
        features_df = pd.DataFrame([{
            "cpu_usage": metrics["cpu"],
            "ram_usage": metrics["ram"],
            "disk_usage": metrics["disk"],
            "disk_read": metrics.get("disk_read", 0),
            "disk_write": metrics.get("disk_write", 0),
            "battery_percent": metrics["battery"],
            "process_count": metrics.get("process_count", 0),
            "heavy_process_count": 0
        }])

        # 4️⃣ Predict system state
        pred, ml_available = predict_system_state(model, features_df)

        # 5️⃣ Basic alert logging
        if pred == 2:
            log_alert(
                alert_type="HANG_RISK",
                source="SYSTEM",
                cpu=metrics["cpu"],
                ram=metrics["ram"],
                disk=metrics["disk"],
                battery=metrics["battery"],
                extra_info="ML" if ml_available else "RULE"
            )

        if metrics["battery"] < 20:
            log_alert(
                alert_type="LOW_BATTERY",
                source="SYSTEM",
                battery=metrics["battery"]
            )

        # 6️⃣ Sleep
        time.sleep(5)

    except Exception as e:
        log_alert(
            alert_type="AGENT_ERROR",
            source="AGENT",
            extra_info=str(e)
        )
        time.sleep(5)