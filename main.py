import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types


load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

locations = ("Локація 1", "Локація 2", "Локація 3", "Локація 4", "Локація 5")


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    await message.answer("Привіт! Почнімо працювати.")
    await message.answer(
        text="Обери одну з п'яти локацій!",
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
            *(types.KeyboardButton(text=location) for location in locations)
        ),
    )


@dp.message_handler(lambda message: message.text and message.text in locations)
async def save_location(message: types.Message):
    """
    This handler will be called when user chose location
    """
    location = message.text
    await message.reply(f"Твою локацію було збережено!")


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
