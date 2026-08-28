from aiogram import Router
from aiogram.types import Message

from app.database.database import Database
from app.services.mute_service import MuteService


router = Router()

database = Database()
mute_service = MuteService(database)


@router.business_message()
async def handle_mutestatus(message: Message):
    connection_id = message.business_connection_id

    if connection_id is None:
        return

    text = (message.text or "").strip().lower()

    if text != ".mutestatus":
        return

    chat_id = message.chat.id

    mute_until = database.get_mute(
        connection_id,
        chat_id
    )

    if not database.is_muted(
        connection_id,
        chat_id
    ):
        await message.answer(
            "🔊 Чат не замьючен."
        )
        return

    if mute_until is None:
        await message.answer(
            "🔇 Чат замьючен навсегда."
        )
        return

    import time

    remaining = mute_until - int(time.time())

    if remaining <= 0:
        database.remove_mute(
            connection_id,
            chat_id
        )

        await message.answer(
            "🔊 Мут уже закончился."
        )

        return

    minutes = remaining // 60
    seconds = remaining % 60

    if minutes > 0:
        text = f"{minutes} мин {seconds} сек"
    else:
        text = f"{seconds} сек"

    await message.answer(
        f"🔇 Чат замьючен.\n\n"
        f"⏱ Осталось: {text}"
    )