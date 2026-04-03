import streamlit as st
import pandas as pd
import os

def render_ids_panel():
    st.subheader("🛡️ Intrusion Detection System")

    log_file = "logs/ids.log"
    if not os.path.exists(log_file):
        st.info("No IDS activity detected yet.")
        return

    df = pd.read_csv(
        log_file,
        sep="|",
        names=["time","event"],
        engine="python"
    )

    alerts = df[df.event.str.contains("ALERT")]

    if alerts.empty:
        st.success("Network traffic is normal.")
    else:
        st.error("⚠️ Intrusion detected!")
        st.dataframe(alerts.tail(10), use_container_width=True)
