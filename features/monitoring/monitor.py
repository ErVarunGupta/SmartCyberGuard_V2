# core/monitor.py

import psutil
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def collect_system_metrics():
    """
    Collects real-time system metrics
    Returns a dictionary
    """

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    disk_io = psutil.disk_io_counters()
    try:
        battery = psutil.sensors_battery()
        battery_pct = battery.percent if battery else 0
    except (FileNotFoundError, NotImplementedError):
        battery_pct = 0

    process_count = len(list(psutil.process_iter()))

    return {
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "disk_read": disk_io.read_bytes,
        "disk_write": disk_io.write_bytes,
        "battery": battery_pct,
        "process_count": process_count
    }

