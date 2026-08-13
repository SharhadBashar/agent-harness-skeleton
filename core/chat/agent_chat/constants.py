import ast
import operator


BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

WEATHER_API = {
    'new york': {
        'city': 'New York',
        'country': 'US',
        'temperature_c': 22.4,
        'feels_like_c': 21.0,
        'condition': 'Partly cloudy',
        'humidity_pct': 58,
        'wind_kph': 14.0,
        'updated_at': '2026-08-13T00:00:00Z',
    },
    'london': {
        'city': 'London',
        'country': 'GB',
        'temperature_c': 16.1,
        'feels_like_c': 14.8,
        'condition': 'Light rain',
        'humidity_pct': 81,
        'wind_kph': 18.5,
        'updated_at': '2026-08-13T00:00:00Z',
    },
    'tokyo': {
        'city': 'Tokyo',
        'country': 'JP',
        'temperature_c': 29.7,
        'feels_like_c': 33.2,
        'condition': 'Humid and sunny',
        'humidity_pct': 72,
        'wind_kph': 9.3,
        'updated_at': '2026-08-13T00:00:00Z',
    },
    'toronto': {
        'city': 'Toronto',
        'country': 'CA',
        'temperature_c': 24.0,
        'feels_like_c': 24.5,
        'condition': 'Clear',
        'humidity_pct': 49,
        'wind_kph': 11.2,
        'updated_at': '2026-08-13T00:00:00Z',
    },
    'sydney': {
        'city': 'Sydney',
        'country': 'AU',
        'temperature_c': 13.6,
        'feels_like_c': 12.1,
        'condition': 'Windy',
        'humidity_pct': 64,
        'wind_kph': 27.8,
        'updated_at': '2026-08-13T00:00:00Z',
    },
}

CITY_ALIASES = {
    'nyc': 'new york',
    'new york city': 'new york',
    'ny': 'new york',
}

SUPPORTED_CITIES = [entry['city'] for entry in WEATHER_API.values()]
