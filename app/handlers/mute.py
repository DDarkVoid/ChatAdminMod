from aiogram import Router
from aiogram.filters import Command

from app.database.database import Database
from app.services.mute_service import MuteService


router = Router()

# База данных.
database = Database()

# Сервис мута.
mute_service = MuteService(database)


@router.message(Command("mute"))
async def mute_command(message):
    """
    Обрабатывает команду /mute.

    Пока используем обычную Telegram-команду:
        /mute
        /mute 30s
        /mute 5m
        /mute 2h
    """

    # Получаем аргументы после команды.
    arguments = message.text.split(maxsplit=1)

    duration = None

    if len(arguments) > 1:
        duration = arguments[1].strip()

    # Пока используем ID пользователя как chat_id.
    chat_id = message.chat.id

    # Временно используем фиксированный connection_id.
    # Настоящий Business Connection подключим позже.
    connection_id = "TEST_CONNECTION"

    try:
        mute_until = mute_service.mute(
            connection_id=connection_id,
            chat_id=chat_id,
            duration=duration
        )

    except ValueError as error:
        await message.answer(
            f"❌ {error}"
        )
        return

    if duration is None:
        await message.answer(
            "🔇 Чат замьючен навсегда."
        )

    else:
        await message.answer(
            f"🔇 Чат замьючен на {duration}."
        )