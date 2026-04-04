import requests

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import QThread, Signal




class ScanWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def run(self):
        try:
            import requests
            res = requests.get(
                "http://127.0.0.1:8000/cleaner/scan",
                timeout=60
            )
            self.finished.emit(res.json())
        except Exception as e:
            self.error.emit(str(e))


class CleanerPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("🧹 Smart AI File Cleaner")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        self.info_label = QLabel("📊 Files: 0 | Selected: 0")
        self.info_label.setStyleSheet("color: #94a3b8;")

        layout.addWidget(self.info_label)


        # =========================
        # BUTTONS
        # =========================
        btn_layout = QHBoxLayout()

        self.scan_btn = QPushButton("🔍 Scan")
        self.delete_btn = QPushButton("🗑 Delete Selected")
        self.select_all_btn = QPushButton("✅ Select All")
        self.delete_all_btn = QPushButton("🔥 Delete All")
        self.preview_btn = QPushButton("👁 Preview")

        self.scan_btn.clicked.connect(self.scan_files)
        self.delete_btn.clicked.connect(self.delete_selected)

        self.select_all_btn.clicked.connect(self.select_all)
        self.delete_all_btn.clicked.connect(self.delete_all)
        self.preview_btn.clicked.connect(self.preview_file)

        btn_layout.addWidget(self.scan_btn)
        btn_layout.addWidget(self.delete_btn)



        btn_layout.addWidget(self.scan_btn)
        btn_layout.addWidget(self.select_all_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.delete_all_btn)
        btn_layout.addWidget(self.preview_btn)

        layout.addLayout(btn_layout)

       

        # =========================
        # TABS
        # =========================
        self.tabs = QTabWidget()

        self.safe_table = self.create_table()
        self.junk_table = self.create_table()
        self.review_table = self.create_table()

        self.tabs.addTab(self.safe_table, "🟢 Safe")
        self.tabs.addTab(self.junk_table, "🟡 Junk")
        self.tabs.addTab(self.review_table, "🔵 Review")

        layout.addWidget(self.tabs)

        self.setLayout(layout)

        self.data = {}

    # =========================
    # TABLE CREATOR
    # =========================
    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Path", "Size (MB)", "Age", "Reason", "Confidence"
        ])

        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.MultiSelection)

        header = table.horizontalHeader()

        header.setStretchLastSection(False)

        header.setSectionResizeMode(0, QHeaderView.Stretch)   # ✅ FIXED
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        table.setWordWrap(False)
        table.setTextElideMode(Qt.ElideMiddle)

        table.itemSelectionChanged.connect(self.update_selected_count)

        return table

    # =========================
    # LOAD DATA INTO TABLE
    # =========================
    def load_table(self, table, files):
        table.setRowCount(len(files))

        for row, f in enumerate(files):
            table.setItem(row, 0, QTableWidgetItem(f["path"]))
            table.setItem(row, 1, QTableWidgetItem(str(f["size"])))
            table.setItem(row, 2, QTableWidgetItem(str(f["age_days"])))
            table.setItem(row, 3, QTableWidgetItem(f["reason"]))
            table.setItem(row, 4, QTableWidgetItem(str(f["confidence"])))

    # =========================
    # SCAN
    # =========================
    def scan_files(self):
        self.scan_btn.setText("Scanning...")
        self.scan_btn.setEnabled(False)

        self.worker = ScanWorker()

        self.worker.finished.connect(self.on_scan_complete)
        self.worker.error.connect(self.on_scan_error)

        self.worker.start()

    # =========================
    # DELETE SELECTED
    # =========================
    def delete_selected(self):
        current_table = self.tabs.currentWidget()

        selected_rows = current_table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.information(self, "Info", "No files selected")
            return

        paths = []

        for row in selected_rows:
            path = current_table.item(row.row(), 0).text()
            paths.append(path)

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {len(paths)} files?"
        )

        if confirm != QMessageBox.Yes:
            return

        try:
            requests.post(
                "http://127.0.0.1:8000/cleaner/clean",
                json={"paths": paths}
            )

            QMessageBox.information(self, "Success", "Files deleted")

            self.scan_files()  # refresh

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


    def select_all(self):
        table = self.tabs.currentWidget()
        table.selectAll()
        self.update_selected_count()


    def delete_all(self):
        table = self.tabs.currentWidget()

        row_count = table.rowCount()

        if row_count == 0:
            QMessageBox.information(self, "Info", "No files available")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete ALL {row_count} files?"
        )

        if confirm != QMessageBox.Yes:
            return

        paths = []

        for row in range(row_count):
            path = table.item(row, 0).text()
            paths.append(path)

        try:
            requests.post(
                "http://127.0.0.1:8000/cleaner/clean",
                json={"paths": paths}
            )

            QMessageBox.information(self, "Success", "All files deleted")
            self.scan_files()

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    
    def update_selected_count(self):
        table = self.tabs.currentWidget()
        selected = len(table.selectionModel().selectedRows())

        total = table.rowCount()

        self.info_label.setText(f"📊 Files: {total} | Selected: {selected}")


    def on_scan_complete(self, data):
        self.scan_btn.setText("🔍 Scan")
        self.scan_btn.setEnabled(True)

        self.data = data

        self.load_table(self.safe_table, data.get("safe", []))
        self.load_table(self.junk_table, data.get("junk", []))
        self.load_table(self.review_table, data.get("review", []))

        total = data["summary"]["total_files"]
        self.info_label.setText(f"📊 Files: {total} | Selected: 0")


    def on_scan_error(self, error):
        self.scan_btn.setText("🔍 Scan")
        self.scan_btn.setEnabled(True)

        QMessageBox.warning(self, "Error", error)

    def preview_file(self):
        table = self.tabs.currentWidget()
        selected_rows = table.selectionModel().selectedRows()

        if not selected_rows:
            QMessageBox.information(self, "Info", "Select a file first")
            return

        # Only preview first selected file
        row = selected_rows[0].row()
        path = table.item(row, 0).text()

        try:
            requests.get(
                "http://127.0.0.1:8000/cleaner/preview",
                params={"path": path}
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))