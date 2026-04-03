import streamlit as st
from features.ai_assistant.ai_assistant import get_ai_response
from features.voice_assistant.input import listen
from features.voice_assistant.output import speak


def render_chatbot():

    st.header("🤖 AI System Assistant")

    # =========================
    # 🔁 CHAT HISTORY
    # =========================
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # =========================
    # 🎨 CSS (MIC INSIDE INPUT)
    # =========================
    st.markdown("""
    <style>
    /* Chat input container */
    div[data-testid="stChatInput"] {
        position: relative;
    }

    /* Mic button styling */
    div[data-testid="stChatInput"] button {
        border-radius: 50% !important;
    }

    /* Adjust spacing so mic looks inside */
    div[data-testid="stChatInput"] input {
        padding-right: 60px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # =========================
    # 💬 DISPLAY CHAT
    # =========================
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # =========================
    # 🎤 MIC BUTTON (OVERLAY STYLE)
    # =========================
    mic_col1, mic_col2 = st.columns([9, 1])

    with mic_col2:
        mic_clicked = st.button("🎤")

    # =========================
    # 💬 CHAT INPUT (UNCHANGED)
    # =========================
    user_input = st.chat_input("Ask about your system...")

    # =========================
    # 🎤 HANDLE VOICE INPUT
    # =========================
    if mic_clicked:
        with st.spinner("Listening..."):
            voice_input = listen()

        if voice_input:
            user_input = voice_input

    # =========================
    # 🚀 PROCESS INPUT
    # =========================
    if user_input:

        # Show user message
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # 🤖 AI RESPONSE
        with st.spinner("Thinking..."):
            response = get_ai_response(user_input)

        clean_response = response.strip().replace("\n", " ")[:]

        # Show AI message
        with st.chat_message("assistant"):
            st.markdown(clean_response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": clean_response
        })

        # 🔊 SPEAK
        speak(clean_response)