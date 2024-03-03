import sys
import os
import wave
import json
from vosk import Model, KaldiRecognizer
import pyaudio

vosk_model_path = "/home/sid/Documents/code/python/voice-assistant/vosk/vosk-model-en-us-0.42-gigaspeech"


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
            result = json.loads(rec.Result())
            print(result["text"])


if __name__ == "__main__":
    main()
