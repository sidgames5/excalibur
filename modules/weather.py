from typing import Optional, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool


import requests

class WeatherInput(BaseModel):
    location_code: str = Field(description="4 letter code (ICAO) of your nearest airport")


class WeatherTool(BaseTool):
    name = "Weather"
    description = "useful for retrieving weather information for a location"
    args_schema: Type[BaseModel] = WeatherInput

    def _run(self, location_code: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        
        weather_data = ""
        # the station should be changed based on the location
        url = "https://aviationweather.gov/cgi-bin/data/metar.php?ids={}&hours=0".format(location_code)
        response = requests.get(url)
        
        return "Weather data in METAR format: " + response.text