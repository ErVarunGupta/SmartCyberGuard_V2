import speech_recognition as sr

WAKE_WORD = "hey"

def listen_for_wake_word():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("👂 Waiting for wake word...")
        recognizer.adjust_for_ambient_noise(source)

        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio).lower()
            print("Heard:", text)

            return WAKE_WORD in text

        except:
            return False