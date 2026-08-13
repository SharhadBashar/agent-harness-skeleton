from pydantic_ai.capabilities import AbstractCapability

from core.stream.convert_weather.prompt import CONVERT_WEATHER_INSTRUCTIONS


class ConvertWeatherCapability(AbstractCapability):
    id = 'convert_weather'
    defer_loading = True

    def get_description(self) -> str:
        return '''
            Use this capability when the user asks to convert weather units.
            The weather lookup returns celsius and kph. Convert when the user wants fahrenheit, mph, or another unit.
            If the user only asks for weather in the default metric units, DO NOT use this capability.
            This capability is only for converting weather values after a city lookup.
            Examples of questions -> "what's the weather in Tokyo in fahrenheit" or "convert London's wind speed to mph"
        '''

    def get_instructions(self) -> str:
        return CONVERT_WEATHER_INSTRUCTIONS
