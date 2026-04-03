from features.voice_assistant.input import listen
from features.voice_assistant.output import speak
from features.ai_assistant.ai_assistant import get_ai_response
from features.monitoring.monitor import collect_system_metrics



def fallback_response(cmd):
    metrics = collect_system_metrics()

    if "cpu" in cmd:
        return f"CPU usage is {metrics['cpu']} percent"

    elif "ram" in cmd:
        return f"RAM usage is {metrics['ram']} percent"

    elif "battery" in cmd:
        return f"Battery is at {metrics['battery']} percent"

    elif "slow" in cmd:
        if metrics["ram"] > 75:
            return "System is slow because RAM usage is high"
        return "System is running fine"

    elif "hello" in cmd:
        return "Hello Varun, I am your AI assistant"

    return None


def start_voice_assistant():
    speak("AI assistant started. You can speak now.")

    while True:
        cmd = listen()

        if not cmd:
            continue

        print("User:", cmd)

        if "exit" in cmd or "stop" in cmd:
            speak("Shutting down assistant")
            break

        # 🧠 AI FIRST
        try:
            response = get_ai_response(cmd)

            if response and len(response.strip()) > 0:
                clean_response = response.strip().replace("\n", " ")
                clean_response = clean_response[:300]

                speak(clean_response)

                import time
                time.sleep(0.5)

                continue

        except Exception as e:
            print("AI error:", e)

        # 🟡 FALLBACK
        fallback = fallback_response(cmd)

        if fallback:
            speak(fallback)
        else:
            speak("Sorry, I did not understand")