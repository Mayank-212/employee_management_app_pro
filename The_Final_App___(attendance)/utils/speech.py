# utils/speech.py

import pyttsx3

def speak(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Text-to-Speech Error: {e}")
