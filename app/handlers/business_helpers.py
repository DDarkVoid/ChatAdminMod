"""Helper functions for business handlers."""

import logging

from aiogram import Bot
from aiogram.methods import DeleteBusinessMessages
from aiogram.types import BusinessBotRights, BusinessConnection

from app.database.database import BusinessConnectionData, Database
from app.services.antispam_service import AntiSpamService

logger = logging.getLogger(__name__)


def get_rights_map(rights: BusinessBotRights | None) -> dict[str, bool]:
    """Extract rights as a dictionary."""
    if rights is None:
        return {
            'reply': False,
            'read_messages': False,
            'delete_sent_messages': False,
            'delete_all_messages': False,
        }

    return {
        'reply': bool(rights.can_reply),
        'read_messages': bool(rights.can_read_messages),
        'delete_sent_messages': bool(rights.can_delete_sent_messages),
        'delete_all_messages': bool(rights.can_delete_all_messages),
    }


def get_missing_rights(connection: BusinessConnection) -> list[str]:
    """Get list of missing rights."""
    rights_map = get_rights_map(connection.rights)
    return [name for name, granted in rights_map.items() if not granted]


def save_connection(database: Database, connection: BusinessConnection) -> None:
    """Save business connection data."""
    rights_map = get_rights_map(connection.rights)
    connection_data = BusinessConnectionData(
        connection_id=connection.id,
        user_id=connection.user.id,
        user_chat_id=connection.user_chat_id,
        is_enabled=connection.is_enabled,
        can_reply=rights_map['reply'],
        can_read_messages=rights_map['read_messages'],
        can_delete_sent_messages=rights_map['delete_sent_messages'],
        can_delete_all_messages=rights_map['delete_all_messages'],
    )
    database.business.save(connection_data)


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
