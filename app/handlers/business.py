"""Business message and connection handlers."""

import logging

from aiogram import Bot, Router
from aiogram.types import BusinessConnection, Message

from app.database.database import BusinessConnectionData, Database
from app.handlers.business_commands import BusinessCommandHandler
from app.handlers.business_helpers import (
    delete_message,
    get_connection,
    get_missing_rights,
    get_right,
    is_antispam_message,
)
from app.services.antispam_service import AntiSpamService
from app.services.mute_service import MuteService

logger = logging.getLogger(__name__)

router = Router()
db = Database()
mute_service = MuteService(db)
antispam_service = AntiSpamService()
command_handler = BusinessCommandHandler(db, mute_service)


def _connection_text(has_missing_rights: bool, language: str | None) -> str:
    """Get connection status text."""
    if has_missing_rights:
        if language == 'en':
            return (
                '<b>ChatAdminMod is not fully connected.</b>\n\n'
                + 'Some required permissions are missing.\n\n'
                + '<b>Required permissions:</b>\n'
                + '• Reply to messages\n'
                + '• Read messages\n'
                + '• Delete sent messages\n'
                + '• Delete received messages\n\n'
                + 'Open the connection settings and enable all required permissions.'
            )
        return (
            '<b>ChatAdminMod подключён не полностью.</b>\n\n'
            + 'Боту выданы не все необходимые права.\n\n'
            + '<b>Необходимые права:</b>\n'
            + '• Ответы на сообщения\n'
            + '• Чтение сообщений\n'
            + '• Удаление отправленных сообщений\n'
            + '• Удаление полученных сообщений\n\n'
            + 'Открой настройки подключения и выдай все необходимые права.'
        )

    if language == 'en':
        return (
            '<b>ChatAdminMod connected successfully.</b>\n\n'
            + 'All required permissions have been granted.\n'
            + 'The bot is ready to work.'
        )
    return (
        '<b>ChatAdminMod успешно подключён.</b>\n\n'
        + 'Все необходимые права выданы.\n'
        + 'Бот готов к работе.'
    )


def _save_connection(connection: BusinessConnection) -> None:
    """Save business connection data."""
    rights = connection.rights
    connection_data = BusinessConnectionData(
        connection_id=connection.id,
        user_id=connection.user.id,
        user_chat_id=connection.user_chat_id,
        is_enabled=connection.is_enabled,
        can_reply=get_right(rights, 'can_reply'),
        can_read_messages=get_right(rights, 'can_read_messages'),
        can_delete_sent_messages=get_right(
            rights,
            'can_delete_sent_messages',
        ),
        can_delete_all_messages=get_right(
            rights,
            'can_delete_all_messages',
        ),
    )
    db.business.save(connection_data)


async def _safe_send_connection_message(
    bot: Bot,
    connection: BusinessConnection,
    text: str,
) -> None:
    """Safely send a connection status message."""
    try:
        await bot.send_message(
            chat_id=connection.user_chat_id,
            text=text,
            parse_mode='HTML',
        )
    except Exception as send_error:
        logger.error(
            '[BUSINESS] Не удалось отправить сообщение: {0}'.format(
                send_error,
            ),
        )


async def _safe_delete_and_log(
    bot: Bot,
    connection_id: str,
    message_id: int,
    chat_id: int,
) -> None:
    """Safely delete a message and log the action."""
    try:
        await delete_message(bot, connection_id, message_id)
    except Exception as delete_error:
        logger.error(
            '[MUTE] Не удалось удалить message {0}: {1}'.format(
                message_id,
                delete_error,
            ),
        )
        return

    logger.info(
        '[MUTE] Deleted message {0} from chat {1}'.format(
            message_id,
            chat_id,
        ),
    )


async def _process_antispam(
    bot: Bot,
    connection_id: str,
    chat_id: int,
    sender_id: int | None,
    message_id: int,
) -> None:
    """Process an antispam trigger."""
    if sender_id is None:
        return
    mute_service.mute(connection_id, chat_id, '30s')
    try:
        await delete_message(bot, connection_id, message_id)
    except Exception as antispam_error:
        logger.error(
            '[ANTISPAM] Ошибка обработки: {0}'.format(antispam_error),
        )
        return

    logger.info(
        '[ANTISPAM] User {0} muted for 30 seconds'.format(sender_id),
    )


@router.business_connection()
async def handle_business_connection(
    connection: BusinessConnection,
    bot: Bot,
) -> None:
    """Handle a new business connection."""
    _save_connection(connection)
    missing_rights = get_missing_rights(connection)
    logger.info('[BUSINESS] Connection: {0}'.format(connection.id))
    logger.info('[BUSINESS] User: {0}'.format(connection.user.id))
    logger.info('[BUSINESS] Enabled: {0}'.format(connection.is_enabled))
    logger.info('[BUSINESS] Missing rights: {0}'.format(missing_rights))

    if not connection.is_enabled:
        return

    language = db.users.find(connection.user.id)
    text = _connection_text(bool(missing_rights), language)
    await _safe_send_connection_message(bot, connection, text)


@router.business_message()
async def handle_business_message(message: Message, bot: Bot) -> None:
    """Handle an incoming business message."""
    connection_id = message.business_connection_id
    if connection_id is None or not (message.text or '').strip():
        return

    connection = await get_connection(bot, connection_id)
    if connection is None:
        return

    _save_connection(connection)
    sender_id = message.from_user.id if message.from_user else None

    if sender_id == connection.user.id:
        await command_handler.process(message, bot)
        return

    if mute_service.is_muted(connection_id, message.chat.id):
        await _safe_delete_and_log(
            bot,
            connection_id,
            message.message_id,
            message.chat.id,
        )
        return

    spam_detected = is_antispam_message(
        db,
        antispam_service,
        connection_id,
        message.chat.id,
        sender_id,
    )
    if spam_detected:
        await _process_antispam(
            bot,
            connection_id,
            message.chat.id,
            sender_id,
            message.message_id,
        )
