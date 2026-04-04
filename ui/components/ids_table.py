from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class IDSTable(QTableWidget):
    def __init__(self):
        super().__init__()

        # =========================
        # 🔥 UPDATED COLUMNS
        # =========================
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels([
            "Time", "Label", "Source IP", "Country",
            "Type", "Risk", "Attack", "Action"
        ])

        header = self.horizontalHeader()
        header.setVisible(True)
        header.setMinimumHeight(35)
        header.setDefaultAlignment(Qt.AlignCenter)

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        self.verticalHeader().setVisible(False)

        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                gridline-color: #334155;
                font-size: 13px;
            }

            QHeaderView::section {
                background-color: #0f172a;
                color: #e2e8f0;
                padding: 8px;
                border: none;
                font-weight: bold;
            }

            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #334155;
            }
        """)

    def update_data(self, logs):
        self.setRowCount(len(logs))

        for row, log in enumerate(logs):
            # =========================
            # DATA ITEMS
            # =========================
            time_item = QTableWidgetItem(log.get("time", ""))
            label_item = QTableWidgetItem(log.get("label", ""))
            ip_item = QTableWidgetItem(log.get("src_ip", ""))
            type_item = QTableWidgetItem(log.get("traffic_type", ""))

            risk_item = QTableWidgetItem(str(log.get("risk_score", "")))
            attack_item = QTableWidgetItem(log.get("attack_type", ""))

            action_item = QTableWidgetItem(log.get("action", ""))
            country_item = QTableWidgetItem(log.get("country", ""))

            # =========================
            # ALIGNMENT
            # =========================
            label_item.setTextAlignment(Qt.AlignCenter)
            type_item.setTextAlignment(Qt.AlignCenter)
            risk_item.setTextAlignment(Qt.AlignCenter)
            action_item.setTextAlignment(Qt.AlignCenter)
            

            label = log.get("label", "").lower()
            action = log.get("action", "").lower()
            risk = log.get("risk_score", 0)

            # =========================
            # 🎨 COLOR LOGIC (IMPROVED)
            # =========================
            if action == "blocked":
                row_color = QColor("#7f1d1d")   # dark red
                text_color = QColor("#fecaca")

            elif label == "attack":
                row_color = QColor("#991b1b")   # red
                text_color = QColor("#fee2e2")

            elif label == "suspicious":
                row_color = QColor("#78350f")   # amber
                text_color = QColor("#fde68a")

            else:
                row_color = QColor("#052e16")   # green
                text_color = QColor("#bbf7d0")

            # =========================
            # APPLY COLORS
            # =========================
            items = [
                time_item, label_item, ip_item,
                type_item, risk_item, attack_item, action_item
            ]

            for item in items:
                item.setBackground(row_color)
                item.setForeground(text_color)

            # =========================
            # 🔥 RISK COLOR OVERRIDE
            # =========================
            if risk >= 80:
                risk_item.setForeground(QColor("#ef4444"))  # red
            elif risk >= 50:
                risk_item.setForeground(QColor("#facc15"))  # yellow
            else:
                risk_item.setForeground(QColor("#22c55e"))  # green

            # =========================
            # BLOCKED LABEL
            # =========================
            if action == "blocked":
                action_item.setText("🚫 BLOCKED")

            # =========================
            # SET ITEMS
            # =========================
            self.setItem(row, 0, time_item)
            self.setItem(row, 1, label_item)
            self.setItem(row, 2, ip_item)
            

            self.setItem(row, 3, country_item)
            self.setItem(row, 4, type_item)
            self.setItem(row, 5, risk_item)
            self.setItem(row, 6, attack_item)
            self.setItem(row, 7, action_item)