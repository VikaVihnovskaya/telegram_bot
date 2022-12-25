import urllib
from enum import IntEnum

import aiohttp

import config


class WeatherServiceException(BaseException):
    pass


class WindDirection(IntEnum):
    North = 0
    Northeast = 45
    East = 90
    Southeast = 135
    South = 180
    Southwest = 225
    West = 270
    Northwest = 315


class WeatherInfo:

    def __init__(self, temperature, location, wind, wind_direction):
        self.temperature = temperature
        self.location = location
        self.wind = wind
        self.wind_direction = wind_direction


async def get_weather_for_city(city_name: str) -> WeatherInfo:
    return await make_weather_service_query(get_city_query_url(city_name))


def get_city_query_url(city_name: str):
    return f'https://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(city_name)}&appid={config.WEATHER_API_KEY}&units=metric&lang=ru'


async def make_weather_service_query(url: str) -> WeatherInfo:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return get_weather_from_response(await resp.json())

    raise WeatherServiceException()


def _parse_wind_speed(openweather_dict: dict) -> float:
    return openweather_dict['wind']['speed']


def _parse_wind_direction(openweather_dict: dict) -> str:
    degrees = openweather_dict['wind']['deg']
    degrees = round(degrees / 45) * 45
    if degrees == 360:
        degrees = 0
    return WindDirection(degrees).name


def get_weather_from_response(openweather_dict):
    return WeatherInfo(openweather_dict['main']['temp'], openweather_dict['name'], _parse_wind_speed(openweather_dict),
                       _parse_wind_direction(openweather_dict))
