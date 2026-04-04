from PySide6.QtWidgets import QMessageBox
import winsound
import time

# Prevent alert spam
LAST_ALERT_TIME = 0


def show_alert(title, message, level="warning", cooldown=10):
    global LAST_ALERT_TIME

    current_time = time.time()

    # 🔥 Cooldown logic (avoid spam)
    if current_time - LAST_ALERT_TIME < cooldown:
        return

    LAST_ALERT_TIME = current_time

    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)

    if level == "critical":
        msg.setIcon(QMessageBox.Critical)
        winsound.Beep(1500, 700)

    elif level == "warning":
        msg.setIcon(QMessageBox.Warning)
        winsound.Beep(1000, 500)

    else:
        msg.setIcon(QMessageBox.Information)

    msg.exec()