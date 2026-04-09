import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget
)
import qtawesome as qta

# ✅ IMPORT FROM SEPARATE FILES (CORRECT WAY)
from ui.pages.system_page import SystemPage
from ui.pages.ids_page import IDSPage
from ui.pages.ai_page import AIPage
from ui.pages.cleaner_page import CleanerPage


# ==============================
# MAIN WINDOW
# ==============================
class SmartGuardApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🛡 SmartGuard Desktop")
        self.setGeometry(100, 100, 1000, 600)

        main_layout = QHBoxLayout()

        # ======================
        # SIDEBAR
        # ======================
        sidebar = QVBoxLayout()

        title = QLabel("⚙ Controls")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        sidebar.addWidget(title)

        # Buttons
        self.btn_system = QPushButton(" System Monitor")
        self.btn_system.setIcon(qta.icon("fa5s.desktop"))

        self.btn_ids = QPushButton(" Intrusion Detection")
        self.btn_ids.setIcon(qta.icon("fa5s.shield-alt"))

        self.btn_cleaner = QPushButton(" File Cleaner")
        self.btn_cleaner.setIcon(qta.icon("fa5s.broom"))

        self.btn_ai = QPushButton(" AI Assistant")
        self.btn_ai.setIcon(qta.icon("fa5s.robot"))

        sidebar.addWidget(self.btn_system)
        sidebar.addWidget(self.btn_ids)
        sidebar.addWidget(self.btn_cleaner)
        sidebar.addWidget(self.btn_ai)

        sidebar.addStretch()

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(220)

        # ======================
        # STACKED PAGES (MAIN CONTENT)
        # ======================
        self.pages = QStackedWidget()

        # ✅ USE IMPORTED PAGES ONLY
        self.pages.addWidget(SystemPage())
        self.pages.addWidget(IDSPage())
        self.pages.addWidget(CleanerPage())
        self.pages.addWidget(AIPage())

        # ======================
        # BUTTON ACTIONS
        # ======================
        self.btn_system.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.btn_ids.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.btn_cleaner.clicked.connect(lambda: self.pages.setCurrentIndex(2))
        self.btn_ai.clicked.connect(lambda: self.pages.setCurrentIndex(3))

        # ======================
        # MAIN LAYOUT
        # ======================
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.pages)

        self.setLayout(main_layout)

        # ======================
        # DARK THEME (PROFESSIONAL)
        # ======================
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: white;
                font-size: 14px;
            }

            QPushButton {
                background-color: #1e293b;
                border: none;
                padding: 12px;
                text-align: left;
                border-radius: 8px;
            }

            QPushButton:hover {
                background-color: #334155;
            }

            QLabel {
                padding: 5px;
            }
        """)


# ==============================
# RUN APP
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartGuardApp()
    window.show()
    sys.exit(app.exec())