import logging
import os

from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
logging.basicConfig(level=logging.INFO)

locations = ("Львів", "Київ", "Харків", "Одеса", "Дніпро")
options = (
    "Все було виконано вчасно",
    "Доступна ціна",
    "Робота на високому рівні",
)
final_options = ("Все чисто", "Залишити коментар")
user_states = ("location_state", "location_done", "checklist_done", "final_option_state", "comment_state")
