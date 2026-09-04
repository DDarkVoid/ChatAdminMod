"""Handler for .mutestatus command."""

import time

from aiogram import Router
from aiogram.types import Message

from app.database.database import Database

router = Router()
database = Database()


def _format_remaining(seconds: int) -> str:
    """Format remaining time."""
    minutes, secs = divmod(seconds, 60)
    if minutes:
        return '{0} min {1} sec'.format(minutes, secs)
    return '{0} sec'.format(secs)


async def _send_status(message: Message, connection_id: str, chat_id: int) -> None:
    """Send mute status."""
    if not database.mutes.exists(connection_id, chat_id):
        await message.answer('🔊 Чат не замьючен.')
        return

    mute_until = database.mutes.find(connection_id, chat_id)
    if mute_until is None:
        await message.answer('🔇 Чат замьючен навсегда.')
        return

    remaining = mute_until - int(time.time())
    if remaining <= 0:
        database.mutes.remove(connection_id, chat_id)
        await message.answer('🔊 Мут уже закончился.')
        return

    time_text = _format_remaining(remaining)
    await message.answer(
        '🔇 Чат замьючен.\n\n⏱ Осталось: {0}'.format(time_text),
    )


@router.business_message()
async def handle_mutestatus(message: Message) -> None:
    """Handle .mutestatus command in business chats."""
    connection_id = message.business_connection_id
    if connection_id is None:
        return

    text = (message.text or '').strip().lower()
    if text != '.mutestatus':
        return

    chat_id = message.chat.id
    await _send_status(message, connection_id, chat_id)
