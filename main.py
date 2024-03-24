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
from duckduckgo_search import DDGS
import urllib.parse

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

# turning this on disables forecasts
# this is useful if you don't need forecasts and don't want to waste your API uses
enable_weather_forecasts = True

personalization_file_path = "./personalization.txt"

# enabling this will print out the amount of time it took to generate the response as well as some other statistics
print_stats = True

# this is the number of threads ollama will use
# i recommend you put 2 less than the number of threads your cpu has
threads = 18


# DO NOT EDIT THE FOLLOWING

import api_keys

weather_api_key = api_keys.weatherapi

# -----------------------------------

client = Client(ollama_url)

global convo_history
convo_history = []

personalization = ""
with open(personalization_file_path, "r") as f:
    personalization = f.read()


accuweather_location_key = 0
latitude = 0
longitude = 0


def send_to_ai(content):
    response = client.chat(
        model=ai_model,
        messages=[
            {"role": "user", "content": content},
        ],
        options={"num_thread": threads},
        stream=False,
    )
    return response["message"]["content"]


def say(text):
    convo_history.append(text)
    if not text_only_mode:
        tts = gTTS(text, lang="en", tld="com")
        tts.save("./tts/speech.mp3")
        os.system("mpg123 ./tts/speech.mp3")
    else:
        print(text)


def main():
    convo_active = False
    convo_no_talk_time = 0
    convo_no_talk_time_limit = 200
    convo_expiry_time_limit = 500

    print("Version: " + version)

    # Set the weather station from location
    ipres = requests.get("http://ip-api.com/json")
    ip = ipres.json()["query"]
    stationresurl = ip_to_airport_url + "/v1?ip=" + ip
    stationres = requests.get(stationresurl)
    weather_station = stationres.text
    print("Weather data will come from airport " + weather_station + " and Weather API")
    print("Weather data may be for the wrong location if you are using a VPN")

    iplocres = requests.get("http://ip-api.com/json")
    latitude = iplocres.json()["lat"]
    longitude = iplocres.json()["lon"]
    posq = urllib.parse.quote(str(latitude) + "," + str(longitude))

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
            data = stream.read(500)
            convo_no_talk_time += 1
            if convo_no_talk_time >= convo_no_talk_time_limit and not text_only_mode:
                convo_active = False
                # print(convo_no_talk_time)
                # print(convo_no_talk_time_limit)
            if convo_no_talk_time >= convo_expiry_time_limit and not text_only_mode:
                # convo_history = []
                pass
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
            if (not wake_word in result) and (not convo_active):
                continue

            convo_active = True
            convo_no_talk_time = 0
            convo_history.append(result)

            current_weather_metar = ""
            current_weather = ""

            url = f"https://aviationweather.gov/cgi-bin/data/metar.php?ids={weather_station}&hours=0"
            response = requests.get(url)
            current_weather_metar = response.text

            resweather = requests.get(
                f"https://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={posq}&days=2&aqi=no&alerts=no"
            )
            current_weather = str(resweather.json())
            current_weather_json = resweather.json()

            current_date_time = datetime.now()
            thours = current_date_time.strftime("%I")
            tmins = current_date_time.strftime("%M")
            tpm = "AM"
            if clock_24_hours:
                tpm = ""
                thours = current_date_time.strftime("%H")
            else:
                tpm = current_date_time.strftime("%p")
            current_time = f"{thours} "
            if tmins == "00":
                current_time = current_time + f"o'clock {tpm}."
            else:
                current_time = current_time + f"{tmins} {tpm}."

            compute_begin_time = datetime.now()

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
                    if "SN" in entry:
                        text_to_say = text_to_say + "and snowy. "
                    elif "RA" in entry:
                        text_to_say = text_to_say + "and rainy. "
                    elif (
                        "OVC" in entry
                        or "BKN" in entry
                        or "SCT" in entry
                        or "FEW" in entry
                    ):
                        text_to_say = text_to_say + "and cloudy. "
                        break
                    elif "CLR" in entry:
                        night = False
                        if int(current_weather_json["current"]["is_day"]) == 0:
                            night = True
                            text_to_say = text_to_say + "and clear. "
                        if not night:
                            text_to_say = text_to_say + "and sunny. "

                if enable_weather_forecasts:
                    hitemp = int(
                        current_weather_json["forecast"]["forecastday"][0]["day"][
                            "maxtemp_f"
                        ]
                    )
                    if not units_imperial:
                        hitemp = (hitemp - 32) / 1.8
                    lowtemp = int(
                        current_weather_json["forecast"]["forecastday"][0]["day"][
                            "mintemp_f"
                        ]
                    )
                    if not units_imperial:
                        lowtemp = (lowtemp - 32) / 1.8

                    iconphrase = current_weather_json["forecast"]["forecastday"][0][
                        "day"
                    ]["condition"]["text"].lower()

                    temp_unit = "celsius"
                    if units_imperial:
                        temp_unit = "fahrenheit"

                    text_to_say = (
                        text_to_say
                        + f"Today it will be {iconphrase} with a low of {lowtemp} degrees {temp_unit} and a high of {hitemp} degrees {temp_unit}."
                    )

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
                    "Respond to the prompt and please keep your response shorter than 50 words. By the way, your name is excalibur. You don't have to announce that your name is excalibur every time I ask you a question. If you need to search the internet, you can! Just write `web_search: <insert the query here>` and nothing else in your response. I repeat, DO NOT INCLUDE ANYTHING BUT THE SEARCH QUERY IN YOUR RESPONSE IF YOU WISH TO PERFORM A WEB SEARCH. DO NOT SAY THAT YOU NEED TO PERFORM A WEB SEARCH AND YOU DON'T HAVE REAL TIME ACCESS, JUST WRITE THE WEB SEARCH PROMPT. If you are able to give a quality answer without using an internet search, DO NOT PUT THE PROMPT FOR A WEB SEARCH. If you do not need to perform a web search, please do not mention it in your response. The same thing goes for if you do need to perform a web search, just don't mention it in your response. And please don't put in the web search prompt if you want the user to search something up. In addition to a web search, you also have the ability to play music. If the user requests to play a playlist, write the following WITH THE EXACT WORDING: `play_playlist: <insert playlist name here>`. If the user does not specify the playlist name, write the following WITH THE EXACT WORDING: `play_music`. I will also provide the conversation history. Please ignore the last element of the list. "
                    + str(convo_history)
                    + " Please do not write anything along the lines of `based on the conversation history` in your response. When you give your response, pretend that you are talking directly to the user. Absolutely DO NOT put any special instructions in your response if the user does not explicitly state to do that. In addition to all of those resources, you can also use the user's personalization file. Please do not write anything along the lines of `based on your preference` in your response. I will also give you the weather data. You may use this weather data in any weather-related question Here is the current weather in METAR format: "
                    + current_weather_metar
                    + ". Here is the 2-day forecast in JSON format: "
                    + current_weather
                    + ". If the user is asking for the weather or a question relating to or involving the weather, please use the prescribed weather data above. Weather questions include things along the lines of `what should I wear` and `what activities should I do`. Do not say anything like `based on the provided weather data and the user's prompt`, instead just get to the point (the weather). The time is currently "
                    + current_time
                    + ". Here is the personalization file: "
                    + personalization
                    + " (end of personalization file). Again, please please PLEASE write your response as if you are directly talking to the user. Now here is the user's prompt: "
                    + result[len(wake_word) :]
                )

                send_to_tts = ""
                if "web\_search" in ai_res.lower() or "web_search" in ai_res.lower():
                    query = ai_res[len(" web\_search") + 2 :]
                    ddgs_res = DDGS().text(query, max_results=5)
                    ai_summary = send_to_ai(
                        "Please summarize the data provided into one or two sentences. The data is formatted in json. Make your response seem like you are answering a question and not summarizing the data. When you are giving your response, pretend that you are directly talking to the user. Here is the data: "
                        + str(ddgs_res)
                    )
                    send_to_tts = ai_summary
                elif ai_res.lower().startswith(" play"):
                    playlist_name = ""
                    if ai_res.lower().startswith(" play\_playlist"):
                        playlist_name = ai_res[len(" play\_playlist: ") :]
                    elif ai_res.lower().startswith(" play\_music"):
                        # TODO: find the user's playlists and select a random one
                        pass
                    else:
                        pass
                else:
                    send_to_tts = ai_res
                compute_end_time = datetime.now()
                if print_stats:
                    print(
                        "Total compute time: "
                        + str(
                            (
                                compute_end_time.timestamp()
                                - compute_begin_time.timestamp()
                            )
                        )
                    )
                say(send_to_tts)

            continue


if __name__ == "__main__":
    main()
