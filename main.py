import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types

from utils import make_report


load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
locations = ("Львів", "Київ", "Харків", "Одеса", "Дніпро")
options = (
    "Все було виконано вчасно",
    "Доступна ціна",
    "Робота на високому рівні",
)
final_options = ("Все чисто", "Залишити коментар")
user_data = {}


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    )
    buttons = (types.KeyboardButton(text=location) for location in locations)
    await message.answer(
        text="Привіт! Почнімо працювати.\nОбери одну з п'яти локацій!",
        reply_markup=keyboard.add(*buttons),
    )


@dp.message_handler(lambda message: message.text and message.text in locations)
async def save_location(message: types.Message):
    """
    This handler will be called when user chose location
    """
    user_id = message.from_user.id
    location = message.text
    user_data[user_id] = dict()
    user_data[user_id]["location"] = location
    user_data[user_id]["checkbox_options"] = {
        option: False for option in options
    }
    await message.reply(f"Твою локацію було збережено!")
    await send_checkbox(user_id)


async def send_checkbox(user_id: int):
    """
    This function will give user a check-list to select options
    """
    keyboard = types.InlineKeyboardMarkup()

    for option, checked in user_data[user_id]["checkbox_options"].items():
        text = f"✅ {option}" if checked else option
        button = types.InlineKeyboardButton(
            text=text, callback_data=f"checkbox_{option}"
        )
        keyboard.add(button)

    button = types.InlineKeyboardButton(
        text="Send", callback_data="checkbox_Send"
    )
    keyboard.add(button)
    await bot.send_message(
        chat_id=user_id,
        text="Обери пункти, які були виконані:",
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda query: query.data.startswith("checkbox_"))
async def process_checkbox_callback(callback_query: types.CallbackQuery):
    """
    This handler will process user's choice from check-list
    """
    selected_option = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id

    if selected_option == "Send":
        checked_options = [
            option
            for option, checked in user_data[user_id][
                "checkbox_options"
            ].items()
            if checked
        ]
        user_data[user_id]["checkbox_options"] = checked_options
        await callback_query.answer(text="Готово!")
        await bot.send_message(
            callback_query.from_user.id,
            f"Готово! Ти обрав(ла) наступні пункти: {', '.join(checked_options)}.",
        )
        await final_option(callback_query.message)
    else:
        user_data[user_id]["checkbox_options"][
            selected_option
        ] = not user_data[user_id]["checkbox_options"][selected_option]
        await callback_query.message.delete()
        await send_checkbox(user_id)


async def final_option(message: types.Message):
    """
    This function will give user a final option to select before summary
    """
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    )
    buttons = (types.KeyboardButton(text=option) for option in final_options)
    await message.answer(
        text="Обери фінальний пункт:",
        reply_markup=keyboard.add(*buttons),
    )


@dp.message_handler(
    lambda message: message.text and message.text in final_options
)
async def process_final_option(message: types.Message):
    """
    This handler will process user's final option
    """
    user_id = message.from_user.id
    selected_final_option = message.text

    if selected_final_option == "Все чисто":
        await get_report(message)
    else:
        await message.answer(
            "Будь ласка, напиши свій коментар:",
        )


@dp.message_handler(
    lambda message: message.text and not message.text.startswith("/")
)
async def process_comment(message: types.Message):
    """
    This function will process user's comment
    """
    user_id = message.from_user.id
    user_data[user_id]["comment"] = message.text
    await message.answer(
        "Тепер можеш завантажити фото, якщо є "
        "або просто введи команду /getreport щоб отримати звіт:"
    )


@dp.message_handler(content_types=["photo"])
async def process_photo(message: types.Message):
    """
    This function will process user's photo
    """
    user_id = message.from_user.id
    photo = message.photo[-1]
    user_data[user_id]["photo"] = photo
    file_path = await bot.get_file(photo.file_id)
    photo_name = f"./{user_id}_photo.jpg"
    user_data[user_id]["photo_name"] = photo_name
    await bot.download_file(file_path.file_path, photo_name)


@dp.message_handler(commands=["getreport"])
async def get_report(message: types.Message):
    user_id = message.from_user.id
    location = user_data[user_id]["location"]
    selected_checkbox_options = user_data[user_id]["checkbox_options"]
    comment = user_data[user_id].get("comment", None)
    photo_name = user_data[user_id].get("photo_name", None)

    # with open(photo_name, "rb") as photo_file:   # TODO: send photo to openai
    #     photo = photo_file

    user_data_for_report = (
        f"\nЛокація: {location}"
        f"\nПункти, які було обрано в чеклисті: {', '.join(selected_checkbox_options)}"
        f"\nКоментар: {comment}"
    )
    await message.answer(
        f"Готово! Твій звіт буде створений на основі наступних даних: {user_data_for_report}"
    )
    report = make_report(user_data_for_report)
    await message.answer(report)


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
