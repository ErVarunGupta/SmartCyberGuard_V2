import streamlit as st
import plotly.express as px
from features.monitoring.data_fetcher import fetch_metrics

def show_analytics():
    st.subheader("📊 System Analytics")

    df = fetch_metrics()

    if df.empty:
        st.warning("No data available yet. Please wait...")
        return

    df = df.sort_values(by="timestamp")

    # CPU Graph
    fig_cpu = px.line(df, x="timestamp", y="cpu", title="CPU Usage (%)")
    st.plotly_chart(fig_cpu, use_container_width=True)

    # RAM Graph
    fig_ram = px.line(df, x="timestamp", y="ram", title="RAM Usage (%)")
    st.plotly_chart(fig_ram, use_container_width=True)

    # Disk Graph
    fig_disk = px.line(df, x="timestamp", y="disk", title="Disk Usage (%)")
    st.plotly_chart(fig_disk, use_container_width=True)

    # Battery Graph
    fig_battery = px.line(df, x="timestamp", y="battery", title="Battery (%)")
    st.plotly_chart(fig_battery, use_container_width=True)