from aiogram import executor, types, Bot, Dispatcher

from config import API_TOKEN, locations, options, final_options, user_states
from utils import make_report


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
user_data = {}
checklist = "checklist_"


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    user_id = message.from_user.id
    user_data[user_id] = dict()

    for state in user_states:
        user_data[user_id][state] = False

    buttons = (types.KeyboardButton(text=location) for location in locations)
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    ).add(*buttons)
    await message.answer(
        text="Привіт! Почнімо працювати.\nОбери одну з п'яти локацій!",
        reply_markup=keyboard,
    )


@dp.message_handler(lambda message: message.text and message.text in locations)
async def process_location(message: types.Message):
    """
    This handler will be called when user chose location
    """
    user_id = message.from_user.id
    location = message.text
    user_data[user_id]["location"] = location
    user_data[user_id]["location_done"] = True
    await message.reply(f"Твою локацію було збережено!")
    user_data[user_id]["checklist_options"] = {
        option: False for option in options
    }
    await send_checklist(user_id)


async def send_checklist(user_id: int):
    """
    This function will give user a check-list to select options
    """
    keyboard = types.InlineKeyboardMarkup()

    for option, checked in user_data[user_id]["checklist_options"].items():
        text = f"✅ {option}" if checked else option
        button = types.InlineKeyboardButton(
            text=text, callback_data=f"checklist_{option}"
        )
        keyboard.add(button)

    keyboard.add(
        types.InlineKeyboardButton(text="Send", callback_data="checklist_Send")
    )
    await bot.send_message(
        chat_id=user_id,
        text="Обери пункти, які були виконані:",
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda query: query.data.startswith(checklist))
async def process_checklist_callback(callback_query: types.CallbackQuery):
    """
    This handler will process user's choice from check-list
    """
    selected_option = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id

    if selected_option == "Send":
        user_data[user_id]["checklist_done"] = True
        checked_options = []

        for option, checked in user_data[user_id]["checklist_options"].items():
            if checked:
                checked_options.append(option)

        user_data[user_id]["checklist_options"] = checked_options
        await callback_query.answer(text="Готово!")
        await bot.send_message(
            user_id,
            f"Готово! Ти обрав(ла) наступні пункти: {', '.join(checked_options)}.",
        )
        await final_option(user_id)
    else:
        user_data[user_id]["checklist_options"][
            selected_option
        ] = not user_data[user_id]["checklist_options"][selected_option]
        await callback_query.message.delete()
        await send_checklist(user_id)


async def final_option(user_id: int):
    """
    This function will give user a final option to select before summary
    """
    buttons = (types.KeyboardButton(text=option) for option in final_options)
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    ).add(*buttons)
    await bot.send_message(
        chat_id=user_id,
        text="Обери фінальний пункт:",
        reply_markup=keyboard,
    )


@dp.message_handler(
    lambda message: message.text and not message.text.startswith("/")
)
async def process_final_option(message: types.Message):
    """
    This handler will process user's final option
    """
    selected_final_option = message.text
    user_id = message.from_user.id

    if selected_final_option == "Все чисто":
        await get_report(message)
    elif selected_final_option == "Залишити коментар":
        user_data[user_id]["comment_state"] = True
        await message.answer(
            "Будь ласка, напиши свій коментар:",
        )
    else:
        await process_comment(message)


@dp.message_handler(
    lambda message: message.text and not message.text.startswith("/")
)
async def process_comment(message: types.Message):
    """
    This function will process user's comment and possible wrong input
    """
    user_id = message.from_user.id

    if not user_data[user_id]["location_done"]:
        await message.answer(
            "Будь ласка, обери локацію написавши команду /start і вибравши її з пропонованого меню."
        )
        return
    if not user_data[user_id]["checklist_done"]:
        await message.answer(
            "Будь ласка, обери пункти з чек листа, вибравши їх з пропонованого меню."
        )
        await send_checklist(user_id)
        return
    if not user_data[user_id]["comment_state"]:
        await message.answer(
            "Будь ласка, обери фінальний пункт з чек листа, вибравши їх з пропонованого меню."
        )
        await final_option(user_id)
        return

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
    file_path = await bot.get_file(photo.file_id)
    photo_name = f"./{user_id}_photo.jpg"
    await bot.download_file(file_path.file_path, photo_name)
    await get_report(message)


@dp.message_handler(commands=["getreport"])
async def get_report(message: types.Message):
    """
    This function will process and generate report for user
    """
    user_id = message.from_user.id
    location = user_data[user_id]["location"]
    selected_checklist_options = user_data[user_id]["checklist_options"]
    comment = user_data[user_id].get("comment", None)
    photo_name = user_data[user_id].get("photo_name", None)

    user_data_for_report = (
        f"\nЛокація: {location}"
        f"\nПункти, які було обрано в чек листі: {', '.join(selected_checklist_options)}"
        f"\nКоментар: {comment}"
    )
    await message.answer(
        f"Готово! Твій звіт буде створений на основі фото (якщо було додано) і наступних даних: {user_data_for_report}"
    )
    report = make_report(user_data_for_report, photo_name)
    await message.answer(report)


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
