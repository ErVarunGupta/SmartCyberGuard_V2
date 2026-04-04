from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class Card(QFrame):
    def __init__(self, title, value="--"):
        super().__init__()

        self.setFixedSize(200, 120)

        # 🔥 Modern styling
        self.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 14px;
                border: 1px solid #334155;
            }
            QFrame:hover {
                border: 1px solid #3b82f6;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Title (small, muted)
        self.title = QLabel(title)
        self.title.setStyleSheet("""
            color: #94a3b8;
            font-size: 12px;
        """)

        # Value (big, bold)
        self.value = QLabel(value)
        self.value.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: white;
        """)

        layout.addWidget(self.title)
        layout.addWidget(self.value)

        self.setLayout(layout)

    def update_value(self, text):
        self.value.setText(text)