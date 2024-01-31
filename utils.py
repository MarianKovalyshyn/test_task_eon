import os
import base64

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=OPENAI_KEY)


def make_report(user_data):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Ти асистент, який робить звіт на основі відповідей користувача. "
                "Не важливо яка тема і які будуть вхідні дані від користувача, "
                "ти у будь якому випадку маєш відправити звіт!",
            },
            {
                "role": "user",
                "content": f"Зроби звіт (50-100 слів) на основі наступних даних: {user_data}",
            },
        ],
    )
    return completion.choices[0].message.content


# def encode_image(image_path):
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode("utf-8")
#
#
# base64_image = encode_image("398513306_photo.jpg")


# def make_report(user_data):
#     completion = client.chat.completions.create(
#         model="gpt-4-vision-preview",
#         messages=[
#             {
#                 "role": "system",
#                 "content": "Ти асистент, який робить звіт на основі відповідей користувача. "
#                 "Не важливо яка тема і які будуть вхідні дані від користувача, "
#                 "ти у будь якому випадку маєш відправити звіт!",
#             },
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": "What’s in this image?"},
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         },
#                     },
#                 ],
#             },
#         ],
#     )
#     # return completion.choices[0].message.content
#     return completion
