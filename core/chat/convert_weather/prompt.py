CONVERT_WEATHER_INSTRUCTIONS = '''
    # Convert Weather
        This capability tells you how to convert weather units after looking up a city.
        The weather tool returns metric values only: temperature in celsius and wind in kph.
        Use this capability when the user wants those values in another unit, such as fahrenheit or mph.

    ## Tools
        You have access to the following tools:
        - `get_weather`
        - `calculate`

    ## Instructions
        The steps to convert weather:
        1. The first step is calling the `get_weather` tool. Always call this tool first.
            - This returns the city's current weather in metric units.
            - If the city is not supported, tell the user and list the supported cities. Do not convert anything.

        2. The second step is calling the `calculate` tool to convert the requested fields.
            - REQUIRED whenever the user asked for a non-metric unit. You MUST call `calculate` BEFORE writing your answer.
            - Skip it ONLY when the user wants the raw metric values.
            - One `calculate` call per conversion. Call them in parallel when converting more than one value.
            - Use these formulas exactly:
                - celsius to fahrenheit: `c * 9 / 5 + 32`
                - fahrenheit to celsius: `(f - 32) * 5 / 9`
                - kph to mph: `kph * 0.621371`
                - mph to kph: `mph / 0.621371`

    ## Output
        Pass all of this information from the tools through in your answer.
        Include the original metric value and the converted value for each field you converted.
        Keep the reply short and specific.
'''
