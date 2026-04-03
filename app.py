import streamlit as st
import sys
import os
import time


import threading
from features.anomaly_detection.network_sniffer import start_sniffing

if "ids_started" not in st.session_state:
    t = threading.Thread(target=start_sniffing, daemon=True)
    t.start()
    st.session_state.ids_started = True

# ===============================
# 🔥 PROJECT ROOT FIX
# ===============================
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Smart System & Security Monitor",
    layout="wide"
)

st.title("🚀 Smart Laptop Analyzer + Cyber Guard")

# ===============================
# IMPORT CORE (FIXED)
# ===============================
from core.database.database import create_table, get_connection
from core.data_logger import log_system_data

# ===============================
# DATABASE INIT
# ===============================
try:
    create_table()
except Exception as e:
    st.error(f"Database Error: {e}")

# ===============================
# GLOBAL LOGGING SYSTEM
# ===============================
if "last_log_time" not in st.session_state:
    st.session_state.last_log_time = 0

if time.time() - st.session_state.last_log_time > 5:
    try:
        log_system_data()
    except Exception as e:
        st.error(f"Logging Error: {e}")
    st.session_state.last_log_time = time.time()

# ===============================
# SIDEBAR
# ===============================
st.sidebar.header("⚙️ Controls")

active_tab = st.sidebar.radio(
    "Select Module",
    [
        "💻 System Monitor",
        "🛡️ Intrusion Detection",
        "🧹 Smart File Cleaner",
        "🤖 AI Assistant"
    ]
)

# Default values
sys_refresh = None
ids_refresh = None
ids_reset = False

# ===============================
# SYSTEM MONITOR SETTINGS
# ===============================
if active_tab == "💻 System Monitor":
    st.sidebar.subheader("💻 System Monitor Settings")

    sys_refresh = st.sidebar.slider(
        "Refresh System Monitor (sec)",
        min_value=3,
        max_value=30,
        value=5,
        step=1
    )

# ===============================
# IDS SETTINGS
# ===============================
elif active_tab == "🛡️ Intrusion Detection":
    st.sidebar.subheader("🛡️ IDS Settings")

    ids_refresh = st.sidebar.slider(
        "Refresh IDS Dashboard (sec)",
        min_value=1,
        max_value=10,
        value=3,
        step=1
    )

    ids_reset = st.sidebar.button("🔄 Reset Monitoring")

# ===============================
# MAIN CONTENT
# ===============================

# 💻 SYSTEM MONITOR
if active_tab == "💻 System Monitor":
    try:
        from ui.dashboard.system_monitor.view import render_system_monitor
        render_system_monitor(refresh_interval=sys_refresh)
    except Exception as e:
        st.error(f"System Monitor Error: {e}")

# 🛡️ IDS
elif active_tab == "🛡️ Intrusion Detection":
    try:
        from ui.dashboard.ids.view import render_ids_dashboard
        render_ids_dashboard(
            refresh_interval=ids_refresh,
            reset_logs=ids_reset
        )
    except Exception as e:
        st.error(f"IDS Error: {e}")

# 🤖 AI ASSISTANT
elif active_tab == "🤖 AI Assistant":
    try:
        from ui.dashboard.chatbot.view import render_chatbot
        render_chatbot()
    except Exception as e:
        st.error(f"AI Assistant Error: {e}")

# 🧹 FILE CLEANER
elif active_tab == "🧹 Smart File Cleaner":
    try:
        from ui.dashboard.file_cleaner.view import render_file_cleaner
        render_file_cleaner()
    except ImportError:
        st.warning("⚠️ File Cleaner module not available.")
    except Exception as e:
        st.error(f"File Cleaner Error: {e}")