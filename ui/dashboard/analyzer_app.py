import os
import sys
import time
import threading
import streamlit as st
import pandas as pd
import joblib

# ===============================
# 🔥 PROJECT ROOT FIX (CORRECT)
# ===============================
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ===============================
# PROJECT IMPORTS
# ===============================
from features.monitoring.monitor import collect_system_metrics
from features.anomaly_detection.network_sniffer import start_sniffing
from core.utils.logger import log_alert   # ✅ FIXED PATH

# ===============================
# STREAMLIT CONFIG
# ===============================
st.set_page_config(
    page_title="SmartCyberGuard",
    layout="wide"
)

st.title("🛡️ SmartCyberGuard – Laptop Health Analyzer")

# ===============================
# LOAD ML MODEL (SAFE)
# ===============================
MODEL = None
MODEL_ERROR = None

try:
    MODEL = joblib.load(os.path.join(PROJECT_ROOT, "models", "model.pkl"))
except Exception as e:
    MODEL_ERROR = str(e)

# ===============================
# SESSION STATE
# ===============================
if "ids_started" not in st.session_state:
    st.session_state.ids_started = False

# ===============================
# IDS THREAD (RUN ONCE)
# ===============================
def start_ids_once():
    if not st.session_state.ids_started:
        t = threading.Thread(target=start_sniffing, daemon=True)
        t.start()
        st.session_state.ids_started = True

        log_alert(
            alert_type="IDS_STARTED",
            source="UI",
            extra_info="IDS thread started"
        )

start_ids_once()

# ===============================
# METRICS FUNCTION
# ===============================
def get_metrics():
    try:
        m = collect_system_metrics()
        return {
            "cpu_usage": m.get("cpu", 0.0),
            "ram_usage": m.get("ram", 0.0),
            "disk_usage": m.get("disk", 0.0),
            "disk_read": m.get("disk_read", 0),
            "disk_write": m.get("disk_write", 0),
            "battery_percent": m.get("battery", 0),
            "process_count": m.get("process_count", 0),
            "heavy_process_count": 0
        }
    except Exception as e:
        log_alert(
            alert_type="METRICS_ERROR",
            source="UI",
            extra_info=str(e)
        )
        return None

# ===============================
# SIDEBAR
# ===============================
refresh = st.sidebar.slider(
    "Refresh interval (seconds)",
    min_value=2,
    max_value=10,
    value=5
)

placeholder = st.empty()

# ===============================
# 🔥 MAIN LOOP (SAFE STREAMLIT WAY)
# ===============================
while True:
    data = get_metrics()

    with placeholder.container():

        if not data:
            st.error("❌ Failed to collect system metrics")
            time.sleep(refresh)
            continue

        df = pd.DataFrame([data])

        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("CPU %", data["cpu_usage"])
        col2.metric("RAM %", data["ram_usage"])
        col3.metric("Disk %", data["disk_usage"])
        col4.metric("Battery %", data["battery_percent"])

        st.subheader("📊 System Metrics")
        st.dataframe(df, use_container_width=True)

        # ML Prediction
        st.subheader("🧠 ML Prediction")

        if MODEL_ERROR:
            st.error(f"❌ ML model not loaded: {MODEL_ERROR}")
        else:
            try:
                pred = MODEL.predict(df)[0]

                state_map = {
                    0: "Normal",
                    1: "High Load",
                    2: "Hang Risk"
                }

                state = state_map.get(pred, "Unknown")

                if pred == 2:
                    st.error(f"🚨 {state}")
                elif pred == 1:
                    st.warning(f"⚠️ {state}")
                else:
                    st.success(f"✅ {state}")

            except Exception as e:
                st.error(f"Prediction failed: {e}")

    time.sleep(refresh)