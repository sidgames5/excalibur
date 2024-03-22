import sys
import os
import wave
import json
from vosk import Model, KaldiRecognizer
import pyaudio
from ollama import Client
from gtts import gTTS
from datetime import datetime
from metar import Metar
import requests

version = "1.1.0-dev"

# ---------- CONFIGURATION ----------

vosk_model_path = (
    "/home/sid/Documents/code/python/voice-assistant/vosk/vosk-model-en-us-0.22"
)

# you can change the wake word to whatever you want
wake_word = "hey excalibur".lower()
# i had a bit of trouble with this wake word as the voice recognition system sometimes picked it up as "pseudo"

# you can use any LLM model supported by ollama
ai_model = "mistral"

# this mode disables voice input and text-to-speech and requires you to type
text_only_mode = True

# should the clock be displayed in 24-hour time (19:44) or 12-hour time (7:44 PM)
clock_24_hours = False

# should units be in imperial
units_imperial = True

# this is the 4 letter code (ICAO) of your nearest airport
# this can be found on https://www.faa.gov/air_traffic/weather/asos
# THIS IS NOT NEEDED ANYMORE
# as long as you have an internet connection you do not need to set the variable
weather_station = "KAGC"
# this is for automatic weather station detection
# you can find the ip to airport server at https://github.com/sidgames5/ip-to-airport
ip_to_airport_url = "http://localhost:3000"

# if you would like to run ollama on a GPU server, you can change the address of the ollama server here
# if you are running ollama locally, there is nothing you have to do
ollama_url = "http://localhost:11434"


# DO NOT EDIT THE FOLLOWING

# import api_keys

# openweather_api_key = api_keys.openweather

# -----------------------------------

client = Client(ollama_url)


def send_to_ai(content):
    response = client.chat(
        model="mistral",
        messages=[
            {"role": "user", "content": content},
        ],
    )
    return response["message"]["content"]


def say(text):
    if not text_only_mode:
        tts = gTTS(text, lang="en", tld="com")
        tts.save("./tts/speech.mp3")
        os.system("mpg123 ./tts/speech.mp3")
    else:
        print(text)


def main():
    print("Version: " + version)

    # Set the weather station from location
    ipres = requests.get("http://ip-api.com/json")
    ip = ipres.json()["query"]
    stationresurl = ip_to_airport_url + "/v1?ip=" + ip
    stationres = requests.get(stationresurl)
    weather_station = stationres.text
    print("Weather data will come from airport " + weather_station)
    print("Weather data may be for the wrong location if you are using a VPN")

    if not text_only_mode:
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

        print("Listening!")
    else:
        print("Ready!")

    while True:
        data = None
        if text_only_mode:
            data = input("Type a prompt: ")
        else:
            data = stream.read(1000)
        if len(data) == 0:
            continue
        if (not text_only_mode and rec.AcceptWaveform(data)) or (text_only_mode):
            result = ""
            if text_only_mode:
                result = wake_word + " " + data
            else:
                r = json.loads(rec.Result())
                result = r["text"]
                print(result)
            if (not wake_word) and (not text_only_mode) in result:
                continue

            if "weather" in result or "temperature" in result:
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
                    elif "FEW" in entry:
                        text_to_say = text_to_say + "with few clouds. "
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
                ai_res = send_to_ai(
                    "Respond to the prompt and please keep your response shorter than 50 words. By the way, your name is excalibur. You don't have to announce that your name is excalibur every time I ask you a question. If you need to search the internet, you can! Just write `web_search: <insert the query here>` and nothing else in your response. I repeat, DO NOT INCLUDE ANYTHING BUT THE SEARCH QUERY IN YOUR RESPONSE IF YOU WISH TO PERFORM A WEB SEARCH. Now here is the user's prompt: "
                    + result[len(wake_word) :]
                )

                send_to_tts = ""
                if ai_res.startswith(" web\_search"):
                    query = ai_res[len(" web\_search") + 2 :]
                else:
                    send_to_tts = ai_res
                say(send_to_tts)
            continue


if __name__ == "__main__":
    main()
