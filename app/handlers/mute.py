from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database.database import Database
from app.services.mute_service import MuteService

router = Router()
database = Database()
mute_service = MuteService(database)


@router.message(Command("mute"))
async def mute_command(message: Message) -> None:
    if message.text is None:
        return

    arguments = message.text.split(maxsplit=1)
    duration = None
    if len(arguments) > 1:
        duration = arguments[1].strip()

    chat_id = message.chat.id
    connection_id = "TEST_CONNECTION"

    try:
        mute_service.mute(connection_id=connection_id, chat_id=chat_id, duration=duration)
    except ValueError as error:
        await message.answer(f"❌ {error}")
        return

    if duration is None:
        await message.answer("🔇 Чат замьючен навсегда.")
    else:
        await message.answer(f"🔇 Чат замьючен на {duration}.")