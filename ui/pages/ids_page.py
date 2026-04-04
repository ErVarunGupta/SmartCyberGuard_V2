import requests
import time

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout
)
from PySide6.QtCore import QTimer, Qt

from ui.components.card import Card
from ui.components.ids_table import IDSTable
from ui.components.block_alert import BlockAlert
from ui.components.traffic_graph import TrafficGraph


class IDSPage(QWidget):
    def __init__(self):
        super().__init__()

        # =========================
        # SCROLL SETUP
        # =========================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(20)

        # =========================
        # TITLE
        # =========================
        title = QLabel("🛡 Cyber Guard IDPS Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        main_layout.addWidget(title)

        # =========================
        # CARDS
        # =========================
        card_layout = QHBoxLayout()

        self.packet_card = Card("Packets")
        self.alert_card = Card("Alerts")
        self.block_card = Card("Blocked IPs")
        self.unique_card = Card("Unique IPs")

        card_layout.addWidget(self.packet_card)
        card_layout.addWidget(self.alert_card)
        card_layout.addWidget(self.block_card)
        card_layout.addWidget(self.unique_card)

        main_layout.addLayout(card_layout)

        # =========================
        # BLOCKED IP LIST
        # =========================
        self.blocked_label = QLabel("🚫 Blocked IPs")
        self.blocked_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.blocked_list = QLabel("None")
        self.blocked_list.setStyleSheet("""
            background-color: #1e293b;
            padding: 10px;
            border-radius: 10px;
        """)

        main_layout.addWidget(self.blocked_label)
        main_layout.addWidget(self.blocked_list)

        # =========================
        # TABLE
        # =========================
        table_title = QLabel("🚨 Live Events")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.table = IDSTable()

        main_layout.addWidget(table_title)

        self.table.setMinimumHeight(250)
        self.table.setMaximumHeight(300)
        main_layout.addWidget(self.table, 1)   # table gets limited space

        # =========================
        # ✅ GRAPH (FIXED POSITION)
        # =========================
        graph_title = QLabel("📊 Traffic Analysis")
        graph_title.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.graph = TrafficGraph()

        main_layout.addWidget(graph_title)
        self.graph.setMinimumHeight(250)
        main_layout.addWidget(self.graph, 2)   # graph gets more space

        # =========================
        # SET SCROLL (AFTER EVERYTHING)
        # =========================
        scroll.setWidget(container)

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll)
        self.setLayout(outer_layout)

        # =========================
        # ALERT CONTROL (FIXED)
        # =========================
        self.alerted_ips = {}   # ip -> last alert time
        self.ALERT_COOLDOWN = 20  # seconds

        # =========================
        # TIMER (CORRECT POSITION)
        # =========================
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(2000)


    # =========================
    # MAIN UPDATE FUNCTION
    # =========================
    def update_data(self):
        try:
            # =========================
            # IDS DATA
            # =========================
            res = requests.get("http://127.0.0.1:8000/ids", timeout=10)
            data = res.json()

            packets = data.get("packets", 0)
            alerts = data.get("alerts", 0)
            blocked = data.get("blocked_ips", 0)
            unique = data.get("unique_ips", 0)

            self.packet_card.update_value(str(packets))
            self.alert_card.update_value(str(alerts))
            self.block_card.update_value(str(blocked))
            self.unique_card.update_value(str(unique))

            logs = data.get("logs", [])[-20:]
            self.table.update_data(logs)

            # =========================
            # BLOCKED IP LIST
            # =========================
            try:
                res_block = requests.get(
                    "http://127.0.0.1:8000/ids/blocked",
                    timeout=10
                )
                ips = res_block.json().get("blocked_ips", [])

                if ips:
                    self.blocked_list.setText("\n".join(ips[:10]))
                else:
                    self.blocked_list.setText("None")

            except Exception as e:
                print("Blocked API Error:", e)

            # =========================
            # 🔥 SMART ALERT (FINAL FIX)
            # =========================
            if not logs:
                return

            latest = logs[-1]

            label = latest.get("label", "")
            ip = latest.get("src_ip", "")
            confidence = latest.get("confidence", 0)

            now = time.time()
            last_time = self.alerted_ips.get(ip, 0)

            # 🚀 ONLY REAL ATTACK + COOLDOWN
            if (
                label == "attack"
                and confidence >= 0.7
                and (now - last_time > self.ALERT_COOLDOWN)
            ):
                attack_type = latest.get("attack_type", "Unknown")
                risk_score = latest.get("risk_score", 0)

                dialog = BlockAlert(ip, attack_type, risk_score)
                dialog.exec()

                self.alerted_ips[ip] = now

        except Exception as e:
            print("IDS API Error:", e)