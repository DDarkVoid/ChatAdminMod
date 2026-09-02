from typing import List, Optional, Any

from aiogram import Bot, Router
from aiogram.methods import DeleteBusinessMessages
from aiogram.types import BusinessConnection, Message

from app.database.database import Database
from app.services.antispam_service import AntiSpamService
from app.services.mute_service import MuteService

router = Router()
db = Database()
mute_service = MuteService(db)
antispam_service = AntiSpamService()


def get_right(rights: Any, name: str) -> bool:
    if rights is None:
        return False
    return bool(getattr(rights, name, False))


def get_missing_rights(connection: BusinessConnection) -> List[str]:
    rights = connection.rights
    missing = []
    if not get_right(rights, "can_reply"):
        missing.append("reply")
    if not get_right(rights, "can_read_messages"):
        missing.append("read_messages")
    if not get_right(rights, "can_delete_sent_messages"):
        missing.append("delete_sent_messages")
    if not get_right(rights, "can_delete_all_messages"):
        missing.append("delete_all_messages")
    return missing


async def delete_message(bot: Bot, connection_id: str, message_id: int) -> None:
    await bot(DeleteBusinessMessages(business_connection_id=connection_id, message_ids=[message_id]))


async def delete_command(bot: Bot, connection_id: str, message_id: int) -> None:
    try:
        await delete_message(bot, connection_id, message_id)
    except Exception as error:
        print(f"[BUSINESS] Не удалось удалить команду: {error}")


async def send_business_text(message: Message, text: str) -> None:
    try:
        await message.answer(text)
    except Exception as error:
        print(f"[BUSINESS] Не удалось отправить ответ: {error}")


async def send_permissions_warning(bot: Bot, connection: BusinessConnection, missing_rights: List[str]) -> None:
    if not missing_rights:
        return
    language = db.get_language(connection.user.id)
    if language == "en":
        text = (
            "<b>ChatAdminMod is not fully connected.</b>\n\n"
            "Some required permissions are missing.\n\n"
            "<b>Required permissions:</b>\n"
            "• Reply to messages\n"
            "• Read messages\n"
            "• Delete sent messages\n"
            "• Delete received messages\n\n"
            "Open the connection settings and enable all required permissions."
        )
    else:
        text = (
            "<b>ChatAdminMod подключён не полностью.</b>\n\n"
            "Боту выданы не все необходимые права.\n\n"
            "<b>Необходимые права:</b>\n"
            "• Ответы на сообщения\n"
            "• Чтение сообщений\n"
            "• Удаление отправленных сообщений\n"
            "• Удаление полученных сообщений\n\n"
            "Открой настройки подключения и выдай все необходимые права."
        )
    try:
        await bot.send_message(chat_id=connection.user_chat_id, text=text, parse_mode="HTML")
    except Exception as error:
        print(f"[BUSINESS] Не удалось отправить предупреждение: {error}")


async def send_connected_message(bot: Bot, connection: BusinessConnection) -> None:
    language = db.get_language(connection.user.id)
    if language == "en":
        text = (
            "<b>ChatAdminMod connected successfully.</b>\n\n"
            "All required permissions have been granted.\n"
            "The bot is ready to work."
        )
    else:
        text = "<b>ChatAdminMod успешно подключён.</b>\n\nВсе необходимые права выданы.\nБот готов к работе."
    try:
        await bot.send_message(chat_id=connection.user_chat_id, text=text, parse_mode="HTML")
    except Exception as error:
        print(f"[BUSINESS] Не удалось отправить сообщение: {error}")


@router.business_connection()
async def handle_business_connection(connection: BusinessConnection, bot: Bot) -> None:
    rights = connection.rights
    can_reply = get_right(rights, "can_reply")
    can_read_messages = get_right(rights, "can_read_messages")
    can_delete_sent_messages = get_right(rights, "can_delete_sent_messages")
    can_delete_all_messages = get_right(rights, "can_delete_all_messages")

    db.save_business_connection(
        connection_id=connection.id,
        user_id=connection.user.id,
        user_chat_id=connection.user_chat_id,
        is_enabled=connection.is_enabled,
        can_reply=can_reply,
        can_read_messages=can_read_messages,
        can_delete_sent_messages=can_delete_sent_messages,
        can_delete_all_messages=can_delete_all_messages,
    )

    missing_rights = get_missing_rights(connection)
    print(f"[BUSINESS] Connection: {connection.id}")
    print(f"[BUSINESS] User: {connection.user.id}")
    print(f"[BUSINESS] Enabled: {connection.is_enabled}")
    print(f"[BUSINESS] Missing rights: {missing_rights}")

    if not connection.is_enabled:
        return

    if missing_rights:
        await send_permissions_warning(bot, connection, missing_rights)
    else:
        await send_connected_message(bot, connection)


@router.business_message()
async def handle_business_message(message: Message, bot: Bot) -> None:
    connection_id = message.business_connection_id
    if connection_id is None:
        return

    chat_id = message.chat.id
    text = (message.text or "").strip()

    try:
        connection = await bot.get_business_connection(business_connection_id=connection_id)
    except Exception as error:
        print(f"[BUSINESS] Не удалось получить connection: {error}")
        return

    db.save_business_connection(
        connection_id=connection.id,
        user_id=connection.user.id,
        user_chat_id=connection.user_chat_id,
        is_enabled=connection.is_enabled,
        can_reply=get_right(connection.rights, "can_reply"),
        can_read_messages=get_right(connection.rights, "can_read_messages"),
        can_delete_sent_messages=get_right(connection.rights, "can_delete_sent_messages"),
        can_delete_all_messages=get_right(connection.rights, "can_delete_all_messages"),
    )

    owner_id = connection.user.id
    sender_id = message.from_user.id if message.from_user else None
    command = text.lower()

    # Команды от владельца
    if sender_id == owner_id:
        if command == ".mute":
            mute_service.mute(connection_id=connection_id, chat_id=chat_id)
            print(f"[MUTE] CHAT {chat_id} muted forever")
            await delete_command(bot, connection_id, message.message_id)
            return

        if command.startswith(".mute "):
            parts = text.split()
            if len(parts) != 2:
                await delete_command(bot, connection_id, message.message_id)
                return
            duration = parts[1].lower()
            try:
                mute_service.mute(connection_id=connection_id, chat_id=chat_id, duration=duration)
            except ValueError as error:
                print(f"[MUTE] {error}")
                await delete_command(bot, connection_id, message.message_id)
                return
            print(f"[MUTE] CHAT {chat_id} muted for {duration}")
            await delete_command(bot, connection_id, message.message_id)
            return

        if command == ".unmute":
            mute_service.unmute(connection_id=connection_id, chat_id=chat_id)
            print(f"[MUTE] CHAT {chat_id} unmuted")
            await delete_command(bot, connection_id, message.message_id)
            return

        if command == ".mutestatus":
            mute_until = db.get_mute(connection_id, chat_id)
            if mute_until is None and not db.is_muted(connection_id, chat_id):
                await send_business_text(message, "🔊 Чат не замьючен.")
            elif mute_until is None:
                await send_business_text(message, "🔇 Чат замьючен навсегда.")
            else:
                import time
                remaining = mute_until - int(time.time())
                if remaining <= 0:
                    db.remove_mute(connection_id, chat_id)
                    await send_business_text(message, "🔊 Мут уже закончился.")
                else:
                    minutes = remaining // 60
                    seconds = remaining % 60
                    time_text = f"{minutes} мин {seconds} сек" if minutes else f"{seconds} сек"
                    await send_business_text(message, f"🔇 Чат замьючен.\n⏱ Осталось: {time_text}")
            await delete_command(bot, connection_id, message.message_id)
            return

        if command == ".antispam":
            enabled = db.is_antispam_enabled(connection_id)
            db.set_antispam(connection_id, not enabled)
            if enabled:
                await send_business_text(message, "Антиспам выключен.")
            else:
                await send_business_text(
                    message,
                    "Антиспам включен.\nПорог: 10 сообщений за 5 секунд.\nМут: 30 секунд."
                )
            await delete_command(bot, connection_id, message.message_id)
            return

    # Сообщения от других пользователей
    if mute_service.is_muted(connection_id=connection_id, chat_id=chat_id):
        try:
            await delete_message(bot, connection_id, message.message_id)
            print(f"[MUTE] Deleted message {message.message_id} from chat {chat_id}")
        except Exception as error:
            print(f"[MUTE] Не удалось удалить message {message.message_id}: {error}")
        return

    if not db.is_antispam_enabled(connection_id) or sender_id is None:
        return

    triggered = antispam_service.check(connection_id=connection_id, chat_id=chat_id, user_id=sender_id)
    if not triggered:
        return

    print(f"[ANTISPAM] Triggered for user {sender_id} in chat {chat_id}")
    try:
        mute_service.mute(connection_id=connection_id, chat_id=chat_id, duration="30s")
        print(f"[ANTISPAM] User {sender_id} muted for 30 seconds")
        await delete_message(bot, connection_id, message.message_id)
    except Exception as error:
        print(f"[ANTISPAM] Ошибка обработки: {error}")