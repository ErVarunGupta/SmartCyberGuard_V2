import streamlit as st


def play_alert_sound():
    st.markdown(
        """
        <audio autoplay>
            <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg">
        </audio>
        """,
        unsafe_allow_html=True
    )


def render_alerts(
    pred,
    hang_alert_enabled,
    alert_interval,
    show_xai=False,
    xai_explanation=None
):
    if pred == 1:
        st.warning("⚠️ System under high load.")

    elif pred == 2 and hang_alert_enabled and alert_interval > 0:
        st.error("🚨 HIGH RISK OF SYSTEM HANG!")
        st.markdown("⏳ **Risk Window:** Next 5–10 minutes")
        st.toast("Hang risk detected! Save your work.", icon="🚨")
        play_alert_sound()

        if show_xai and xai_explanation:
            with st.expander("🧠 Why this was detected?"):
                for label, percent in xai_explanation:
                    st.write(f"• **{label}** ({percent}%)")
