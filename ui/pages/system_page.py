import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QScrollArea
from PySide6.QtCore import QTimer, Qt, QThread, Signal

from ui.components.card import Card
from ui.components.process_table import ProcessTable


# =========================
# WORKER THREAD (IMPORTANT)
# =========================
class SystemWorker(QThread):
    data_fetched = Signal(dict)

    def run(self):
        try:
            res = requests.get("http://127.0.0.1:8000/metrics", timeout=10)
            self.data_fetched.emit(res.json())
        except Exception as e:
            print("System API Error:", e)
            self.data_fetched.emit({})


class SystemPage(QWidget):
    def __init__(self):
        super().__init__()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)

        title = QLabel("💻 System Performance Monitor")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # CARDS
        card_layout = QHBoxLayout()
        self.cpu_card = Card("CPU %")
        self.ram_card = Card("RAM %")
        self.disk_card = Card("Disk %")
        self.battery_card = Card("Battery %")

        card_layout.addWidget(self.cpu_card)
        card_layout.addWidget(self.ram_card)
        card_layout.addWidget(self.disk_card)
        card_layout.addWidget(self.battery_card)

        layout.addLayout(card_layout)

        # STATE
        self.state_label = QLabel("State: --")
        self.health_label = QLabel("Health Score: --")

        layout.addWidget(self.state_label)
        layout.addWidget(self.health_label)

        # RECOMMENDATIONS
        self.recommend_box = QLabel("Loading...")
        self.recommend_box.setStyleSheet("background:#1e293b; padding:10px; border-radius:10px;")

        layout.addWidget(QLabel("🛠 Recommended Actions"))
        layout.addWidget(self.recommend_box)

        # PROCESS TABLE
        layout.addWidget(QLabel("🔥 Top Processes"))
        self.process_table = ProcessTable()
        layout.addWidget(self.process_table)

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        self.worker = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_data)
        self.timer.start(3000)

    def fetch_data(self):
        if self.worker and self.worker.isRunning():
            return

        self.worker = SystemWorker()
        self.worker.data_fetched.connect(self.update_ui)
        self.worker.start()

    def update_ui(self, data):
        if not data:
            return

        self.cpu_card.update_value(f"{data.get('cpu', 0):.1f}")
        self.ram_card.update_value(f"{data.get('ram', 0):.1f}")
        self.disk_card.update_value(f"{data.get('disk', 0):.1f}")
        self.battery_card.update_value(f"{data.get('battery', 0):.0f}")

        self.state_label.setText(f"State: {data.get('state', '--')}")
        self.health_label.setText(f"Health Score: {data.get('health_score', '--')}")

        rec = data.get("recommendation", [])
        self.recommend_box.setText("\n".join(rec))

        self.process_table.update_data(data.get("top_processes", []))