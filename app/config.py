import os

from dotenv import load_dotenv


# Загружаем переменные из файла .env
load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден! "
        "Открой файл .env и укажи токен Telegram-бота."
    )