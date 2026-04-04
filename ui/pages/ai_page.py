import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea
)
from PySide6.QtCore import Qt


class AIPage(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        title = QLabel("🤖 AI System Assistant")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title)

        # =========================
        # CHAT AREA
        # =========================
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)

        container = QWidget()
        container.setLayout(self.chat_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        main_layout.addWidget(scroll)

        # =========================
        # INPUT
        # =========================
        input_layout = QHBoxLayout()

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Ask about your system...")

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_box)
        input_layout.addWidget(send_btn)

        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

    # =========================
    # ADD MESSAGE
    # =========================
    def add_message(self, text, is_user=True):
        label = QLabel(text)
        label.setWordWrap(True)

        if is_user:
            label.setStyleSheet("background:#2563eb; padding:8px; border-radius:8px;")
            label.setAlignment(Qt.AlignRight)
        else:
            label.setStyleSheet("background:#1e293b; padding:8px; border-radius:8px;")
            label.setAlignment(Qt.AlignLeft)

        self.chat_layout.addWidget(label)

    # =========================
    # SEND MESSAGE
    # =========================
    def send_message(self):
        msg = self.input_box.text().strip()

        if not msg:
            return

        self.add_message(msg, True)
        self.input_box.clear()

        try:
            res = requests.post(
                "http://127.0.0.1:8000/ai",
                json={"message": msg}
            )
            data = res.json()

            reply = data["response"]

        except Exception as e:
            reply = f"Error: {e}"

        self.add_message(reply, False)