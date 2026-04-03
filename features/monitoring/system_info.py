import psutil

def collect_system_metrics():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else 0
    }