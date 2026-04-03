import os
import sys
import time
import winsound
from plyer import notification
from core.utils.logger import read_latest_alert

# -------------------------------------------------
# ADD PROJECT ROOT TO PATH
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)



SEEN = set()

def notify(alert: str):
    winsound.Beep(1200, 600)
    notification.notify(
        title="🛡 SmartCyberGuard Alert",
        message=alert,
        timeout=6
    )

print("🔔 Alert notifier started (listening for REAL threats only)")

while True:
    alert = read_latest_alert()

    if not alert:
        time.sleep(2)
        continue

    if alert in SEEN:
        time.sleep(2)
        continue

    alert_lower = alert.lower()

    # ❌ Ignore normal traffic
    if "normal" in alert_lower:
        SEEN.add(alert)
        time.sleep(2)
        continue

    # ❌ Ignore self traffic
    if "src_ip=10." in alert_lower or "src_ip=192.168." in alert_lower:
        SEEN.add(alert)
        time.sleep(2)
        continue

    # ✅ REAL ALERT
    notify(alert)
    SEEN.add(alert)

    time.sleep(2)
