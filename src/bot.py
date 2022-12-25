import logging

from aiogram import Bot, Dispatcher, executor, types

import bot_messages
import config
from src.api_service import WeatherServiceException, get_weather_for_city, WeatherInfo

WEATHER_RETRIEVAL_FAILED_MESSAGE = bot_messages.get_message('weather_for_location_retrieval_failed')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.reply(bot_messages.get_message('help'), reply=False)


@dp.message_handler(content_types=['text'])
async def get_weather_in_city(message: types.Message):
    try:
        weather: WeatherInfo = await get_weather_for_city(message.text)
    except WeatherServiceException:
        await message.reply(WEATHER_RETRIEVAL_FAILED_MESSAGE)
        return

    response = bot_messages.get_message('weather_in_city_message') \
        .format(weather.location,  weather.temperature, weather.wind_direction, weather.wind) + '\n\n'

    await message.reply(response)


@dp.message_handler()
async def default_response(message: types.Message):
    await message.reply(bot_messages.get_message('general_failure'))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
