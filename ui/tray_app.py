import pystray
from pystray import MenuItem as item
from PIL import Image
import subprocess
import os
import sys
import webbrowser
import time

# ============================
# PATH FIX (IMPORTANT)
# ============================
if hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================
# FILE PATHS
# ============================
APP = os.path.join(BASE_DIR, "app.py")
BG_EXE = os.path.join(BASE_DIR, "background_monitor.exe")

ICON = os.path.join(BASE_DIR, "assets", "icon.png")

# ============================
# GLOBAL PROCESS LIST
# ============================
processes = []

# ============================
# START BACKGROUND SERVICE
# ============================
def start_background():
    try:
        if os.path.exists(BG_EXE):
            p = subprocess.Popen([BG_EXE])
            processes.append(p)
        else:
            print("Background EXE not found")
    except Exception as e:
        print("Error starting background:", e)

# ============================
# OPEN DASHBOARD (STREAMLIT)
# ============================


def open_dashboard(icon, item):
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(project_root, "app.py")

        python_path = os.path.join(project_root, "venv", "Scripts", "python.exe")

        # 🔥 Start Streamlit
        subprocess.Popen(
            [python_path, "-m", "streamlit", "run", app_path],
            cwd=project_root
        )

        # wait for server
        time.sleep(5)

        # 🔥 FORCE open browser (Windows)
        subprocess.Popen(
            ["cmd", "/c", "start", "http://localhost:8501"],
            shell=True
        )

    except Exception as e:
        print("Error:", e)
# ============================
# EXIT APP
# ============================
def exit_app(icon, item):
    for p in processes:
        try:
            p.kill()
        except:
            pass

    icon.stop()
    os._exit(0)

# ============================
# SETUP TRAY
# ============================
def setup_tray():
    try:
        image = Image.open(ICON)
    except:
        # fallback icon
        image = Image.new("RGB", (64, 64), color="blue")

    menu = (
        item("📊 Open Dashboard", open_dashboard),
        item("❌ Exit", exit_app),
    )

    icon = pystray.Icon(
        "SmartCyberGuard",
        image,
        "Smart Cyber Guard",
        menu
    )

    # start background first
    start_background()

    icon.run()

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    setup_tray()