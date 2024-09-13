vosk_model_path = "/home/sid/Documents/code/python/voice-assistant/vosk/vosk-model-en-us-0.22"

# you can change the wake word to whatever you want
wake_word = "hey excalibur"

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
debug = True

# this is the number of threads ollama will use
# i recommend you put 2 less than the number of threads your cpu has
threads = 18

# Home assistant integration is optional
home_assistant_integration = True
# You should be able to use either your local URL or your Nabu Casa URL
hass_url = "http://10.0.1.152:8123"
hass_access_token = ""