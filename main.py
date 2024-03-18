import sys
import os
import wave
import json
from vosk import Model, KaldiRecognizer
import pyaudio
import ollama
from gtts import gTTS

version = "0.1.0"

# ---------- CONFIGURATION ----------

vosk_model_path = "/home/sid/Documents/code/python/voice-assistant/vosk/vosk-model-en-us-0.42-gigaspeech"

# you can change the wake word to whatever you want
wake_word = "hey sudo".lower()
# i had a bit of trouble with this wake word as the voice recognition system sometimes picked it up as "pseudo"

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


def say(text):
    tts = gTTS(text, lang="en", tld="com")
    tts.save("./tts/speech.mp3")
    os.system("mpg123 ./tts/speech.mp3")
    print("debug: done talking")


# DEBUGGING NOTES
# "done talking" does not get printed even after it is done talking


def main():
    print("Version: " + version)

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
            print(result[len(wake_word) :])
            say(
                send_to_ai(
                    "Respond to the prompt and please keep your response shorter than 50 words: "
                    + result[len(wake_word) :]
                )
            )
            continue


if __name__ == "__main__":
    main()
