"""Configuration module."""

import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError(
        'BOT_TOKEN not found! Open the .env file and specify the Telegram bot token.',
    )
