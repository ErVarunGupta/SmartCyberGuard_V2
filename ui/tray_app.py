import pystray
from pystray import MenuItem as item
from PIL import Image
import subprocess
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PYTHONW = os.path.join(ROOT, "venv", "Scripts", "pythonw.exe")
PYTHON = os.path.join(ROOT, "venv", "Scripts", "python.exe")

BG_MONITOR = os.path.join(ROOT, "services", "background_monitor.py")
ALERT = os.path.join(ROOT, "services", "alert_notifier.py")
APP = os.path.join(ROOT, "app.py")
ICON = os.path.join(ROOT, "assets", "icon.png")

processes = []

def start_background():
    processes.append(subprocess.Popen([PYTHONW, BG_MONITOR]))
    processes.append(subprocess.Popen([PYTHONW, ALERT]))

def open_dashboard():
    subprocess.Popen([PYTHON, "-m", "streamlit", "run", APP])

def exit_app(icon, item):
    for p in processes:
        p.kill()
    icon.stop()
    sys.exit()

def setup_tray():
    image = Image.open(ICON)
    menu = (
        item("📊 Open Dashboard", open_dashboard),
        item("❌ Exit", exit_app),
    )

    icon = pystray.Icon("SmartCyberGuard", image, "Smart Cyber Guard", menu)
    start_background()
    icon.run()

if __name__ == "__main__":
    setup_tray()
