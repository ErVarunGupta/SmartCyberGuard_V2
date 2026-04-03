# dashboard/components/tables.py

import streamlit as st
import psutil
import pandas as pd

# ---------------- PROCESS → APP NAME MAP ----------------
PROCESS_APP_MAP = {
    "chrome.exe": "Google Chrome",
    "Code.exe": "Visual Studio Code",
    "python.exe": "Python Application",
    "msedgewebview2.exe": "Microsoft Edge (Background)",
    "taskmgr.exe": "Task Manager",
    "Taskmgr.exe": "Task Manager",
    "MsMpEng.exe": "Windows Defender",
    "dwm.exe": "Windows Display Manager",
    "System Idle Process": "System Idle (CPU Free)",
    "explorer.exe": "File Explorer"
}

# -------------------------------------------------------
def get_top_heavy_processes(limit=5):
    """
    Returns DataFrame of top CPU-consuming applications
    """
    rows = []

    for proc in psutil.process_iter(
        ['name', 'cpu_percent', 'memory_percent']
    ):
        try:
            name = proc.info['name']
            cpu = proc.info['cpu_percent']
            mem = proc.info['memory_percent']

            if cpu and cpu > 1:
                app_name = PROCESS_APP_MAP.get(name, name)
                rows.append([
                    app_name,
                    name,
                    round(cpu, 1),
                    round(mem, 2)
                ])
        except:
            pass

    df = pd.DataFrame(
        rows,
        columns=["Application", "Process", "CPU %", "RAM %"]
    )

    if df.empty:
        return df

    return df.sort_values("CPU %", ascending=False).head(limit)


# -------------------------------------------------------
def render_resource_table(df):
    """
    Renders top resource consuming apps table
    """
    st.subheader("🔥 Top Resource-Consuming Applications")

    if df.empty:
        st.info("No heavy applications detected.")
    else:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
