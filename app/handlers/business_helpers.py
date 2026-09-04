"""Helper functions for business handlers."""

import logging

from aiogram import Bot
from aiogram.methods import DeleteBusinessMessages
from aiogram.types import BusinessBotRights, BusinessConnection, Message

from app.database.database import Database
from app.services.antispam_service import AntiSpamService

logger = logging.getLogger(__name__)

RIGHTS_MAP = (
    ('can_reply', 'reply'),
    ('can_read_messages', 'read_messages'),
    ('can_delete_sent_messages', 'delete_sent_messages'),
    ('can_delete_all_messages', 'delete_all_messages'),
)


def get_right(rights: BusinessBotRights | None, name: str) -> bool:
    """Check if right exists."""
    return bool(getattr(rights, name, False))


def get_missing_rights(connection: BusinessConnection) -> list[str]:
    """Get list of missing rights."""
    rights = connection.rights
    return [
        label
        for attr, label in RIGHTS_MAP
        if not get_right(rights, attr)
    ]


async def get_connection(
    bot: Bot,
    connection_id: str,
) -> BusinessConnection | None:
    """Get business connection."""
    try:
        return await bot.get_business_connection(
            business_connection_id=connection_id,
        )
    except Exception as connection_error:
        logger.error(
            '[BUSINESS] Failed to get connection: {0}'.format(
                connection_error,
            ),
        )
        return None


def is_antispam_message(
    database: Database,
    antispam_service: AntiSpamService,
    connection_id: str,
    chat_id: int,
    user_id: int | None,
) -> bool:
    """Check if antispam triggered."""
    if user_id is None:
        return False
    if not database.antispam.find(connection_id):
        return False
    return antispam_service.check(connection_id, chat_id, user_id)


async def delete_message(
    bot: Bot,
    connection_id: str,
    message_id: int,
) -> None:
    """Delete message via Business API."""
    await bot(
        DeleteBusinessMessages(
            business_connection_id=connection_id,
            message_ids=[message_id],
        ),
    )


async def delete_command(
    bot: Bot | None,
    connection_id: str | None,
    message_id: int,
) -> None:
    """Delete command with missing context handling."""
    if bot is None or connection_id is None:
        return

    try:
        await delete_message(bot, connection_id, message_id)
    except Exception as delete_error:
        logger.error(
            '[BUSINESS] Failed to delete command: {0}'.format(
                delete_error,
            ),
        )


async def send_business_text(message: Message, text: str) -> None:
    """Send reply in business chat."""
    try:
        await message.answer(text)
    except Exception as send_error:
        logger.error(
            '[BUSINESS] Failed to send reply: {0}'.format(
                send_error,
            ),
        )
