# --------------------------------
# SmartCyberGuard Background Agent (AI Powered)
# --------------------------------

# ===== SINGLE INSTANCE (WINDOWS MUTEX) =====
import sys
import ctypes

kernel32 = ctypes.windll.kernel32

mutex = kernel32.CreateMutexW(
    None,
    True,
    "SmartCyberGuard_BackgroundMonitor"
)

ERROR_ALREADY_EXISTS = 183

if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
    sys.exit(0)

# ===== STANDARD IMPORTS =====
import os
import time
import threading
import pandas as pd
import joblib

# ===== PATH HANDLING =====
if hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ===== PROJECT IMPORTS =====
from features.monitoring.monitor import collect_system_metrics
from features.ai_assistant.predictor import predict_system_state
from features.anomaly_detection.network_sniffer import start_sniffing
from features.ai_assistant.ai_brain import analyze
# from core.action_engine import execute
# from core.voice.output import speak
from core.logger.logger import log_alert

# from utils.data_logger import log_system_data

# ===== RESOURCE PATH =====
def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(BASE_DIR, relative_path)

# ===== LOAD ML MODEL =====
model = None
try:
    model = joblib.load(resource_path("models/model.pkl"))
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

# ===== START IDS THREAD =====
ids_thread = threading.Thread(
    target=start_sniffing,
    daemon=True
)
ids_thread.start()

log_alert(
    alert_type="IDS_STARTED",
    source="AGENT",
    extra_info="IDS running"
)

# ===== SPEAK CONTROL (ANTI-SPAM) =====
LAST_SPOKEN = ""
LAST_SPOKEN_TIME = 0
SPEAK_COOLDOWN = 15  # seconds

def safe_speak(message):
    global LAST_SPOKEN, LAST_SPOKEN_TIME

    now = time.time()

    # prevent repeating same message
    if message == LAST_SPOKEN and (now - LAST_SPOKEN_TIME < SPEAK_COOLDOWN):
        return

    LAST_SPOKEN = message
    LAST_SPOKEN_TIME = now

    speak(message)

# ===== MAIN LOOP =====
print("🚀 SmartCyberGuard AI Agent Started")

while True:
    try:
        # 1️⃣ Collect metrics
        metrics = collect_system_metrics()

        log_system_data(metrics)

        # 2️⃣ Prepare ML features
        features_df = pd.DataFrame([{
            "cpu_usage": metrics["cpu"],
            "ram_usage": metrics["ram"],
            "disk_usage": metrics["disk"],
            "disk_read": metrics["disk_read"],
            "disk_write": metrics["disk_write"],
            "battery_percent": metrics["battery"],
            "process_count": metrics["process_count"],
            "heavy_process_count": 0
        }])

        # 3️⃣ Predict system state
        pred, ml_available = predict_system_state(model, features_df)

        # 4️⃣ Intrusion flag (basic for now)
        intrusion_detected = False   # future: connect with IDS output

        # 5️⃣ AI BRAIN DECISION
        message, actions = analyze(metrics, pred, intrusion_detected)

        # 6️⃣ Speak intelligently
        safe_speak(message)

        # 7️⃣ Execute actions
        for action in actions:
            execute(action)

        # 8️⃣ Logging important events
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

        # 9️⃣ Wait
        time.sleep(5)

    except Exception as e:
        log_alert(
            alert_type="AGENT_ERROR",
            source="AGENT",
            extra_info=str(e)
        )
        time.sleep(5)