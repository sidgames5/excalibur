import sys
import os
import wave
import json
from vosk import Model, KaldiRecognizer
import pyaudio
import ollama
from gtts import gTTS
from datetime import datetime
from metar import Metar
import requests

from agent import agent_executor

version = "0.1.1"

def send_to_ai(content):
    return agent_executor.invoke({"input": content})["output"]


def say(text):
    tts = gTTS(text, lang="en", tld="com")
    tts.save("./tts/speech.mp3")
    os.system("mpg123 ./tts/speech.mp3")
    print("debug: done talking")


# DEBUGGING NOTES
# "done talking" does not get printed even after it is done talking

def main():
    print("Version: " + version)

    model = Model(os.environ.get("VOSK_MODEL_PATH"))
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
            if not os.environ.get("WAKE_WORD") in result:
                continue

            say(send_to_ai(result[len(os.environ.get("WAKE_WORD")):]))


if __name__ == "__main__":
    main()
