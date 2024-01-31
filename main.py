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
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = (types.KeyboardButton(text=location) for location in locations)
    await message.answer("Привіт! Почнімо працювати.")
    await message.answer(
        text="Обери одну з п'яти локацій!",
        reply_markup=keyboard.add(*buttons),
    )


@dp.message_handler(lambda message: message.text and message.text in locations)
async def save_location(message: types.Message):
    """
    This handler will be called when user chose location
    """
    location = message.text
    await message.reply(f"Твою локацію було збережено!")
    await send_checkbox(message)


checkbox_states = {
    option: False for option in ("Option 1", "Option 2", "Option 3")
}


async def send_checkbox(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()

    for option, checked in checkbox_states.items():
        text = f"✅ {option}" if checked else option
        button = types.InlineKeyboardButton(
            text=text, callback_data=f"checkbox_{option}"
        )
        keyboard.add(button)

    button = types.InlineKeyboardButton(
        text="Send", callback_data="checkbox_Send"
    )
    keyboard.add(button)
    await message.answer(text="Select options:", reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("checkbox_"))
async def process_checkbox_callback(callback_query: types.CallbackQuery):
    selected_option = callback_query.data.split("_")[1]

    if selected_option == "Send":
        checked_options = [
            option for option, checked in checkbox_states.items() if checked
        ]
        await callback_query.answer(text="Done!")
        await bot.send_message(
            callback_query.from_user.id,
            f"Done! You selected: {', '.join(checked_options)}",
        )
    else:
        checkbox_states[selected_option] = not checkbox_states[selected_option]
        await callback_query.message.delete()
        await send_checkbox(callback_query.message)


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
