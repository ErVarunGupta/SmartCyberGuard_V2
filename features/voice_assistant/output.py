import pyttsx3

engine = pyttsx3.init()

engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def speak(text):
    if not text:
        return

    try:
        print("AI:", text)

        engine.stop()   # 🔥 reset engine
        engine.say(str(text))
        engine.runAndWait()

    except Exception as e:
        print("Voice error:", e)