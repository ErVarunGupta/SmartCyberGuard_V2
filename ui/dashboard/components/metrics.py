import streamlit as st


def render_metrics(cpu, ram, disk, battery):
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("CPU %", f"{cpu:.1f}")
    c2.metric("RAM %", f"{ram:.1f}")
    c3.metric("Disk %", f"{disk:.1f}")
    c4.metric(
        "Battery %",
        f"{battery:.0f}" if battery != -1 else "N/A"
    )
