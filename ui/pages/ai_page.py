import requests
import threading
import re

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QTimer

API_URL = "http://127.0.0.1:8000/ai"


# =========================
# USER MESSAGE (RIGHT)
# =========================
class UserBubble(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setWordWrap(True)
        self.setMaximumWidth(400)

        self.setStyleSheet("""
            background-color: #ef4444;
            color: white;
            padding: 10px 14px;
            border-radius: 16px;
            font-size: 14px;
        """)


# =========================
# AI RESPONSE (FULL WIDTH + FORMATTED)
# =========================
class AIMessage(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setWordWrap(True)

        formatted = self.format_text(text)
        self.setText(formatted)

        self.setStyleSheet("""
            color: #e5e7eb;
            font-size: 15px;
            padding: 10px 40px;
        """)

    def format_text(self, text):
        # Remove markdown stars
        text = text.replace("**", "")

        # Add spacing
        text = text.replace("\n", "<br><br>")

        # Highlight percentages
        text = re.sub(r'(\d+\.?\d*%)',
                      r'<b style="color:#22c55e">\1</b>', text)

        # Headings
        text = text.replace("Primary Bottlenecks:",
                            "<b style='color:#f87171'>🚨 Primary Bottlenecks:</b>")
        text = text.replace("Actionable Suggestions:",
                            "<b style='color:#60a5fa'>💡 Actionable Suggestions:</b>")

        return text


# =========================
# MAIN PAGE
# =========================
class AIPage(QWidget):
    response_signal = Signal(str)

    def __init__(self):
        super().__init__()

        self.mode = "GEMINI"
        self.is_voice_query = False

        self.response_signal.connect(self.display_response)

        main_layout = QVBoxLayout(self)

        # =========================
        # TITLE
        # =========================
        title = QLabel("🤖 AI System Assistant")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        main_layout.addWidget(title)

        # =========================
        # MODE BUTTONS
        # =========================
        mode_layout = QHBoxLayout()

        self.gemini_btn = QPushButton("Gemini AI")
        self.smart_btn = QPushButton("Smart AI")

        self.gemini_btn.clicked.connect(self.set_gemini)
        self.smart_btn.clicked.connect(self.set_smart)

        mode_layout.addWidget(self.gemini_btn)
        mode_layout.addWidget(self.smart_btn)

        main_layout.addLayout(mode_layout)

        self.update_mode_ui()

        # =========================
        # CHAT AREA
        # =========================
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border:none")

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(20)

        self.scroll.setWidget(self.chat_widget)
        main_layout.addWidget(self.scroll)

        # =========================
        # THINKING LABEL
        # =========================
        self.thinking_label = QLabel("")
        self.thinking_label.setAlignment(Qt.AlignCenter)
        self.thinking_label.setStyleSheet("color: gray; font-size: 14px;")
        main_layout.addWidget(self.thinking_label)

        self.thinking_timer = QTimer()
        self.thinking_timer.timeout.connect(self.animate_thinking)
        self.thinking_step = 0

        # =========================
        # MIC STATUS
        # =========================
        self.mic_label = QLabel("")
        self.mic_label.setAlignment(Qt.AlignCenter)
        self.mic_label.setStyleSheet("color: #22c55e; font-size: 14px;")
        main_layout.addWidget(self.mic_label)

        # =========================
        # INPUT BAR
        # =========================
        input_layout = QHBoxLayout()

        self.input = QTextEdit()
        self.input.setFixedHeight(45)
        self.input.setPlaceholderText("Ask anything...")

        self.input.setStyleSheet("""
            background-color: #1f2937;
            border-radius: 20px;
            padding: 10px;
        """)

        self.voice_btn = QPushButton("🎤")
        self.voice_btn.clicked.connect(self.voice_input)

        send_btn = QPushButton("➤")
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input)
        input_layout.addWidget(self.voice_btn)
        input_layout.addWidget(send_btn)

        main_layout.addLayout(input_layout)

    # =========================
    # MODE SWITCH
    # =========================
    def set_gemini(self):
        self.mode = "GEMINI"
        self.update_mode_ui()

    def set_smart(self):
        self.mode = "SMART"
        self.update_mode_ui()

    def update_mode_ui(self):
        if self.mode == "GEMINI":
            self.gemini_btn.setStyleSheet("background:#2563eb; color:white; padding:8px; border-radius:10px;")
            self.smart_btn.setStyleSheet("background:#1f2937; color:white; padding:8px; border-radius:10px;")
        else:
            self.smart_btn.setStyleSheet("background:#2563eb; color:white; padding:8px; border-radius:10px;")
            self.gemini_btn.setStyleSheet("background:#1f2937; color:white; padding:8px; border-radius:10px;")

    # =========================
    # ADD USER
    # =========================
    def add_user(self, text):
        layout = QHBoxLayout()
        bubble = UserBubble(text)

        layout.addStretch()
        layout.addWidget(bubble)

        wrapper = QWidget()
        wrapper.setLayout(layout)

        self.chat_layout.addWidget(wrapper)

    # =========================
    # ADD AI
    # =========================
    def add_ai(self, text):
        ai = AIMessage(text)
        self.chat_layout.addWidget(ai)

    # =========================
    # THINKING ANIMATION
    # =========================
    def animate_thinking(self):
        dots = ["⏳ Thinking", "⏳ Thinking.", "⏳ Thinking..", "⏳ Thinking..."]
        self.thinking_label.setText(dots[self.thinking_step % len(dots)])
        self.thinking_step += 1

    # =========================
    # SEND MESSAGE
    # =========================
    def send_message(self):
        user_text = self.input.toPlainText().strip()
        if not user_text:
            return

        self.add_user(user_text)
        self.input.clear()

        # Start thinking animation
        self.thinking_label.setText("⏳ Thinking...")
        self.thinking_timer.start(500)

        threading.Thread(
            target=self.get_response,
            args=(user_text,),
            daemon=True
        ).start()

    # =========================
    # API CALL
    # =========================
    def get_response(self, message):
        try:
            res = requests.post(API_URL, json={
                "message": message,
                "mode": self.mode
            }, timeout=50)

            data = res.json()
            reply = data.get("response", "No response")

        except Exception as e:
            reply = f"❌ Error: {str(e)}"

        self.response_signal.emit(reply)

    # =========================
    # DISPLAY RESPONSE
    # =========================
    def display_response(self, reply):
        self.thinking_timer.stop()
        self.thinking_label.setText("")

        self.add_ai(reply)

        if self.is_voice_query:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(reply)
                engine.runAndWait()
            except:
                pass

        self.is_voice_query = False

    # =========================
    # VOICE INPUT
    # =========================
    def voice_input(self):
        import speech_recognition as sr

        recognizer = sr.Recognizer()

        self.mic_label.setText("🎙 Listening...")
        self.voice_btn.setText("🟥")

        try:
            with sr.Microphone() as source:
                audio = recognizer.listen(source, timeout=5)

            text = recognizer.recognize_google(audio)

            self.mic_label.setText("")
            self.voice_btn.setText("🎤")

            self.input.setText(text)
            self.is_voice_query = True

            self.send_message()

        except:
            self.mic_label.setText("❌ Voice not recognized")
            self.voice_btn.setText("🎤")