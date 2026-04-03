import streamlit as st
import json
import os


def load_sidebar_settings(settings_path):
    with open(settings_path, "r") as f:
        settings = json.load(f)

    st.sidebar.header("⚙️ Alert Settings")

    hang_alert_enabled = st.sidebar.toggle(
        "Enable Hang Alerts",
        value=settings["hang_alert_enabled"],
        key="hang_alert_toggle"
    )

    alert_interval = st.sidebar.selectbox(
        "Alert Interval (seconds)",
        options=[30, 60, 0],
        index=[30, 60, 0].index(settings["alert_interval"])
    )

    battery_threshold = st.sidebar.selectbox(
        "Battery High Threshold (%)",
        options=[70, 80, 90],
        index=[70, 80, 90].index(settings["battery_high_threshold"])
    )

    new_settings = {
        "hang_alert_enabled": hang_alert_enabled,
        "alert_interval": alert_interval,
        "battery_high_threshold": battery_threshold
    }

    if new_settings != settings:
        with open(settings_path, "w") as f:
            json.dump(new_settings, f, indent=2)

    return new_settings
