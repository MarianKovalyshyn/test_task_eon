import base64

from openai import OpenAI

from config import OPENAI_KEY


client = OpenAI(api_key=OPENAI_KEY)


def make_report(user_data, photo_name=None):
    base64_image = encode_image(photo_name) if photo_name else None
    payload_user_content = [
        {
            "type": "text",
            "text": f"Зроби звіт на основі наступних даних {user_data} і фото (якщо є):",
        },
    ]

    if base64_image:
        payload_user_content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        )

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Ти асистент, який робить професійний звіт на основі відповідей користувача "
                "і відправляю цьому ж користувачу цей звіт. Не важливо які будуть вхідні дані від користувача, "
                "ти у будь якому випадку маєш відправити сформований звіт на приблизно 50-100 слів!",
            },
            {
                "role": "user",
                "content": payload_user_content,
            },
        ],
    )
    return completion.choices[0].message.content


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
