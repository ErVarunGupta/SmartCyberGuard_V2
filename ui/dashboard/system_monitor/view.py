import streamlit as st
import joblib
import pandas as pd
import os
import time
import plotly.express as px

from core.data_logger import log_system_data
from features.monitoring.monitor import collect_system_metrics
from features.ai_assistant.predictor import predict_system_state
from core.utils.logger import log_alert

from ui.dashboard.components.metrics import render_metrics
from ui.dashboard.components.tables import get_top_heavy_processes, render_resource_table
from ui.dashboard.components.alerts import render_alerts
from ui.dashboard.components.sidebar import load_sidebar_settings

from features.monitoring.data_fetcher import fetch_metrics

# -------------------------------
# 🔥 SAFE FALLBACK FUNCTIONS
# -------------------------------
def calculate_health_score(cpu, ram, disk, pred):
    score = 100 - (cpu * 0.3 + ram * 0.3 + disk * 0.2)
    if pred == 2:
        score -= 20
    score = max(0, int(score))

    if score < 50:
        label = "Poor"
    elif score < 80:
        label = "Average"
    else:
        label = "Good"

    return score, label


def get_auto_mitigation_suggestions(cpu, ram, disk, pred, battery):
    suggestions = []

    if cpu > 80:
        suggestions.append("Close high CPU usage apps")
    if ram > 80:
        suggestions.append("Restart system or close apps")
    if disk > 90:
        suggestions.append("Free up disk space")
    if battery < 20:
        suggestions.append("Plug in charger")

    if not suggestions:
        suggestions.append("System is stable")

    return suggestions


# -------------------------------
# PATHS
# -------------------------------
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")
SETTINGS_PATH = os.path.join(BASE_DIR, "core", "config", "settings.json")

LABEL_MAP = {
    0: "🟢 Normal",
    1: "🟡 High Load",
    2: "🔴 Hang Risk"
}


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def render_system_monitor(refresh_interval=5):

    st.header("💻 System Performance Monitor")

    # 🔥 SAFE SETTINGS LOAD
    try:
        settings = load_sidebar_settings(SETTINGS_PATH)
    except:
        settings = {
            "hang_alert_enabled": True,
            "alert_interval": 5
        }

    # -------------------------------
    # LOAD ML MODEL
    # -------------------------------
    model = None
    try:
        model = joblib.load(MODEL_PATH)
    # except Exception as e:
    #     st.error(f"ML ERROR: {e}")
    except:
        st.warning("⚠️ ML model not available, using rule-based prediction")

    # -------------------------------
    # SESSION STATE INIT
    # -------------------------------
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = 0

    if "cached_metrics" not in st.session_state:
        st.session_state.cached_metrics = None

    # -------------------------------
    # DATA UPDATE
    # -------------------------------
    if time.time() - st.session_state.last_refresh > refresh_interval:

        metrics = collect_system_metrics()
        st.session_state.cached_metrics = metrics

        log_system_data()

        st.session_state.last_refresh = time.time()

    # -------------------------------
    # UI RENDER
    # -------------------------------
    metrics = st.session_state.cached_metrics

    if metrics is None:
        st.warning("⏳ Collecting system data...")
        return

    cpu = metrics["cpu"]
    ram = metrics["ram"]
    disk = metrics["disk"]
    battery = metrics["battery"]
    process_count = metrics["process_count"]

    # -------------------------------
    # HEAVY PROCESSES
    # -------------------------------
    heavy_df = get_top_heavy_processes()
    heavy_process_count = len(heavy_df)

    # -------------------------------
    # FEATURE VECTOR
    # -------------------------------
    features = pd.DataFrame([{
        "cpu_usage": cpu,
        "ram_usage": ram,
        "disk_usage": disk,
        "disk_read": metrics["disk_read"],
        "disk_write": metrics["disk_write"],
        "battery_percent": battery,
        "process_count": process_count,
        "heavy_process_count": heavy_process_count
    }])

    # -------------------------------
    # PREDICTION
    # -------------------------------
    pred, ml_available = predict_system_state(model, features)
    state = LABEL_MAP.get(pred, "Unknown")

    # -------------------------------
    # HEALTH SCORE
    # -------------------------------
    health_score, health_label = calculate_health_score(cpu, ram, disk, pred)

    # -------------------------------
    # UI METRICS
    # -------------------------------
    render_metrics(cpu, ram, disk, battery)

    st.markdown(f"### Current State: **{state}**")

    st.markdown(
        f"""
        ### 🧠 System Health Score  
        **{health_score}/100 — {health_label}**
        """
    )

    # -------------------------------
    # ALERTS
    # -------------------------------
    render_alerts(
        pred=pred,
        hang_alert_enabled=settings.get("hang_alert_enabled", True),
        alert_interval=settings.get("alert_interval", 5),
        show_xai=False
    )

    # -------------------------------
    # LOG ALERT
    # -------------------------------
    if pred == 2 and settings.get("hang_alert_enabled", True):
        log_alert(
            alert_type="HANG_RISK",
            cpu=cpu,
            ram=ram,
            disk=disk,
            battery=battery,
            extra_info="ML" if ml_available else "RULE"
        )

    # -------------------------------
    # RECOMMENDATIONS
    # -------------------------------
    st.subheader("🛠️ Recommended Actions")

    suggestions = get_auto_mitigation_suggestions(cpu, ram, disk, pred, battery)
    for s in suggestions:
        st.write(f"• {s}")

    # -------------------------------
    # RESOURCE TABLE
    # -------------------------------
    render_resource_table(heavy_df)

    # -------------------------------
    # ANALYTICS
    # -------------------------------
    st.subheader("📊 Analytics Dashboard")

    df = fetch_metrics()

    if df is not None and not df.empty:

        df = df.sort_values("timestamp")

        fig = px.line(
            df,
            x="timestamp",
            y=["cpu", "ram", "disk"],
            title="System Usage Over Time"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("📊 No historical data yet. Please wait 10–20 seconds...")