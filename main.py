import sys
import os
import wave
import json
from vosk import Model, KaldiRecognizer
import pyaudio
import ollama
import pyttsx3

version = "0.1.0"

vosk_model_path = "/home/sid/Documents/code/python/voice-assistant/vosk/vosk-model-en-us-0.42-gigaspeech"

# you can change the wake word to whatever you want
wake_word = "hey ai".lower()


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
    return


def main():
    print("Version: " + version)
    ttsengine = pyttsx3.init()
    ttsengine.setProperty("rate", 125)

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

    while True:
        print("Listening")
        data = stream.read(2000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            r = json.loads(rec.Result())
            result = r["text"]
            print(result)
            if not wake_word in result:
                continue
            action = send_to_ai(
                "Which thing is the user trying to do: turn on the tv (tv_on), turn on the lights (lights_on), asking a question or giving a query (question), other (other), unable to understand the prompt (invalid). Answer with respective alias provided: "
                + result
            )
            print(action)
            if "tv_on" in action:
                say("You do not have a TV connected.")
                continue
            if "lights_on" in action:
                say("You do not have any lights connected.")
                continue
            if "question" in action:
                say(send_to_ai(result))
                continue

            if "invalid" in action:
                say("I didn't understand that.")
                continue

            if "other" in action:
                say("I'm sorry but I don't have the ability to do this yet.")
                continue


if __name__ == "__main__":
    main()
