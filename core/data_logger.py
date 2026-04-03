from features.monitoring.system_info import collect_system_metrics
from core.database.database import get_connection

def log_system_data():
    data = collect_system_metrics()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO metrics (cpu, ram, disk, battery)
    VALUES (?, ?, ?, ?)
    """, (data["cpu"], data["ram"], data["disk"], data["battery"]))

    conn.commit()
    conn.close()