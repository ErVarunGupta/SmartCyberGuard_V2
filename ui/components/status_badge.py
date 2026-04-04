from PySide6.QtWidgets import QLabel


def get_status_badge(state: str):
    label = QLabel(f" {state} ")

    if state == "Normal":
        bg = "#22c55e"   # green
    elif state == "Moderate":
        bg = "#f59e0b"   # yellow
    else:
        bg = "#ef4444"   # red

    label.setStyleSheet(f"""
        background-color: {bg};
        color: black;
        padding: 6px 12px;
        border-radius: 12px;
        font-weight: bold;
    """)

    return label