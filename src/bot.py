import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Update, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

import bot_messages
import config
from src.api_service import WeatherServiceException, get_weather_for_city, WeatherInfo

WEATHER_RETRIEVAL_FAILED_MESSAGE = bot_messages.get_message('weather_for_location_retrieval_failed')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher(bot)
callback_types = CallbackData('type', 'action')


@dp.message_handler(commands=['start'])
async def start(message:  types.Message):
    current_weather_button = InlineKeyboardButton(text="Показать текущую погоду в городе \U0001F324",
                                                  callback_data=callback_types.new(action='CURRENT_WEATHER'))
    reply_markup = InlineKeyboardMarkup().add(current_weather_button)
    await message.reply(text="Выберите:", reply_markup=reply_markup)


@dp.message_handler(commands=['help'])
async def start(message: types.Message):
    await message.reply(bot_messages.get_message('help'), reply=False)


async def button(update: Update) -> None:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")


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


@dp.callback_query_handler(callback_types.filter(action='CURRENT_WEATHER'))
async def handle_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, (bot_messages.get_message('enter_city')))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
