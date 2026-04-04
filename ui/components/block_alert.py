from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
import requests
import winsound


class BlockAlert(QDialog):
    def __init__(self, ip, attack_type="Unknown", risk_score=0):
        super().__init__()

        self.ip = ip
        self.attack_type = attack_type
        self.risk_score = risk_score

        self.setWindowTitle("🚨 Intrusion Detected")
        self.setFixedWidth(350)

        # 🔊 SOUND ALERT
        try:
            winsound.Beep(1000, 400)
        except:
            pass

        layout = QVBoxLayout()

        # =========================
        # 🔥 UPDATED LABEL
        # =========================
        label = QLabel(
            f"🚨 Threat Detected!\n\n"
            f"IP: {self.ip}\n"
            f"Type: {self.attack_type}\n"
            f"Risk: {self.risk_score}/100"
        )
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 14px;")

        layout.addWidget(label)

        # =========================
        # BUTTONS
        # =========================
        btn_layout = QHBoxLayout()

        self.ok_btn = QPushButton("OK")
        self.block_btn = QPushButton("BLOCK")

        self.block_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
        """)

        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.block_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # ACTIONS
        self.ok_btn.clicked.connect(self.accept)
        self.block_btn.clicked.connect(self.block_ip)

    def block_ip(self):
        try:
            requests.post(
                "http://127.0.0.1:8000/ids/block",
                json={"ip": self.ip},
                timeout=5
            )
        except Exception as e:
            print("Block API Error:", e)

        self.accept()