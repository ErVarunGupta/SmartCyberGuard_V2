from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt


class ProcessTable(QTableWidget):
    def __init__(self):
        super().__init__()

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Process", "CPU %", "RAM %"])

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    # ✅ FIXED FUNCTION
    def update_data(self, processes):
        self.setRowCount(len(processes))

        for row, p in enumerate(processes):
            name = QTableWidgetItem(str(p.get("name", "")))
            cpu = QTableWidgetItem(str(p.get("cpu", "")))
            ram = QTableWidgetItem(str(p.get("ram", "")))

            self.setItem(row, 0, name)
            self.setItem(row, 1, cpu)
            self.setItem(row, 2, ram)