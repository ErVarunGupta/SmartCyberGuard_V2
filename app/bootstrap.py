from services.monitor_service import start_monitoring
from services.alert_service import start_alerts
from ui.tray_app import start_tray

def start_app():
    print("🚀 Starting Smart Laptop Analyzer...")
    
    start_monitoring()
    start_alerts()
    start_tray()