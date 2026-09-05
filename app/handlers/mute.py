"""Handler for /mute command."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database.database import Database
from app.services.mute_service import MuteService

router = Router()
database = Database()
mute_service = MuteService(database)


@router.message(Command('mute'))
async def mute_command(message: Message) -> None:
    """Handle /mute command."""
    if message.text is None:
        return

    arguments = message.text.split(maxsplit=1)
    duration = arguments[1].strip() if len(arguments) > 1 else None
    chat_id = message.chat.id
    connection_id = 'TEST_CONNECTION'

    try:
        mute_service.mute(
            connection_id=connection_id,
            chat_id=chat_id,
            duration=duration,
        )
    except ValueError as error:
        await message.answer('❌ {0}'.format(error))
        return

    if duration is None:
        await message.answer('🔇 Чат замьючен навсегда.')
    else:
        await message.answer('🔇 Чат замьючен на {0}.'.format(duration))
