import sys
import os
import wave
import json
from vosk import Model, KaldiRecognizer
import pyaudio
import ollama

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


def main():
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
        data = stream.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            r = json.loads(rec.Result())
            result = r["text"]
            if not wake_word in result:
                continue
            action = send_to_ai(
                "Which thing is the user trying to do: turn on the tv (tv_on), turn on the lights (lights_on), ask a question (question), other (other). Answer with respective alias provided: "
                + result
            )
            print(action)
            if "other" in action:
                print("I'm sorry but I don't have the ability to do this yet.")
            if "tv_on" in action:
                print("You do not have a TV connected.")
            if "lights_on" in action:
                print("You do not have any lights connected.")
            if "question" in action:
                print(send_to_ai(result))


if __name__ == "__main__":
    main()
