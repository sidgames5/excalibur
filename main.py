import sys
import os
import wave
import json
from vosk import Model, KaldiRecognizer
import pyaudio
import ollama
import pyttsx3

version = "0.1.0"

# ---------- CONFIGURATION ----------

vosk_model_path = "/home/sid/Documents/code/python/voice-assistant/vosk/vosk-model-en-us-0.42-gigaspeech"

# you can change the wake word to whatever you want
wake_word = "hey sudo".lower()

ai_model = "mistral"
# you can use any LLM model supported by ollama

# -----------------------------------


def send_to_ai(content):
    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "user", "content": content},
        ],
    )
    return response["message"]["content"]


ttsengine = pyttsx3.init(driverName="espeak")


def say(text):
    ttsengine.say(text)
    ttsengine.runAndWait()
    print("debug: done talking")


# DEBUGGING NOTES
# "done talking" does not get printed even after it is done talking


def main():
    print("Version: " + version)
    ttsengine = pyttsx3.init()
    ttsengine.setProperty("rate", 100)

    model = Model(vosk_model_path)
    rec = KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8000,
    )

    print("Listening")

    while True:
        data = stream.read(2000)
        if len(data) == 0:
            continue
        if rec.AcceptWaveform(data):
            r = json.loads(rec.Result())
            result = r["text"]
            print(result)
            if not wake_word in result:
                continue
            say(send_to_ai(result))
            continue


if __name__ == "__main__":
    main()
