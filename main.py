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

version = "0.1.0"

# ---------- CONFIGURATION ----------

vosk_model_path = "/home/sid/Documents/code/python/voice-assistant/vosk/vosk-model-en-us-0.42-gigaspeech"

# you can change the wake word to whatever you want
wake_word = "hey sudo".lower()
# i had a bit of trouble with this wake word as the voice recognition system sometimes picked it up as "pseudo"

# you can use any LLM model supported by ollama
ai_model = "mistral"

# should the clock be displayed in 24-hour time (19:44) or 12-hour time (7:44 PM)
clock_24_hours = False

# should units be in imperial
units_imperial = True

# this is the 4 letter code (ICAO) of your nearest airport
# this can be found on https://www.faa.gov/air_traffic/weather/asos
weather_station = "KAGC"


# DO NOT EDIT THE FOLLOWING

import api_keys

# openweather_api_key = api_keys.openweather

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

            if "weather" in result:
                weather_data = ""
                # the station should be changed based on the location
                url = f"https://aviationweather.gov/cgi-bin/data/metar.php?ids={weather_station}&hours=0"
                response = requests.get(url)
                weather_data = response.text
                obs = Metar.Metar(f"METAR {weather_data}")

                temp = 0
                if units_imperial:
                    temp = round((obs.temp.value() * 1.8) + 32)
                sky = obs.sky
                conditions = obs.weather

                text_to_say = f"It is currently {temp} degrees "

                if units_imperial:
                    text_to_say = text_to_say + "fahrenheit "
                else:
                    text_to_say = text_to_say + "celsius "

                for entry in sky:
                    if "OVC" in entry:
                        text_to_say = text_to_say + "and cloudy. "
                        break
                    elif "BKN" in entry:
                        text_to_say = text_to_say + "with broken clouds. "
                        break
                    elif "SCT" in entry:
                        text_to_say = text_to_say + "with scattered clouds. "
                        break
                    elif "CLR" in entry:
                        night = False
                        if obs.time.hour >= 18 or obs.time.hour <= 6:
                            night = True
                        if not night:
                            text_to_say = text_to_say + "and sunny. "

                ecount = 0
                for entry in conditions:
                    if ecount == 0:
                        text_to_say = text_to_say + "There is currently "
                    else:
                        text_to_say = text_to_say + "and "

                    ecount += 1

                    if "-" in entry:
                        text_to_say = text_to_say + "light "
                    elif "+" in entry:
                        text_to_say = text_to_say + "heavy "
                    else:
                        text_to_say = text_to_say + "moderate "

                    if "SN" in entry:
                        text_to_say = text_to_say + "snow "
                    elif "RA" in entry:
                        text_to_say = text_to_say + "rain "
                    elif "GR" in entry:
                        text_to_say = text_to_say + "hail "
                    elif "BR" in entry:
                        text_to_say = text_to_say + "mist "

                say(text_to_say)
            elif "time" in result:
                # Get the current date and time
                current_date_time = datetime.now()

                # Format the current time with AM/PM
                thours = current_date_time.strftime("%I")
                tmins = current_date_time.strftime("%M")
                tpm = "AM"
                if clock_24_hours:
                    tpm = ""
                    thours = current_date_time.strftime("%H")
                else:
                    tpm = current_date_time.strftime("%p")
                text_to_say = f"The time is currently {thours} "
                if tmins == "00":
                    text_to_say = text_to_say + f"o'clock {tpm}."
                else:
                    text_to_say = text_to_say + f"{tmins} {tpm}."
                say(text_to_say)
            else:
                say(
                    send_to_ai(
                        "Respond to the prompt and please keep your response shorter than 50 words: "
                        + result[len(wake_word) :]
                    )
                )
            continue


if __name__ == "__main__":
    main()
