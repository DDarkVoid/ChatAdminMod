"""Business connection helper functions."""

import logging
from typing import TypedDict

from aiogram import Bot
from aiogram.types import BusinessBotRights, BusinessConnection

from app.database.database import BusinessConnectionData, Database
from app.services.antispam_service import AntiSpamService

logger = logging.getLogger(__name__)


class RightsDict(TypedDict):
    """Business connection rights structure."""

    can_reply: bool
    can_read_messages: bool
    can_delete_sent_messages: bool
    can_delete_all_messages: bool


def _extract_rights(rights: BusinessBotRights | None) -> RightsDict:
    """Extract rights explicitly without dynamic getattr."""
    if rights is None:
        return {
            'can_reply': False,
            'can_read_messages': False,
            'can_delete_sent_messages': False,
            'can_delete_all_messages': False,
        }

    return {
        'can_reply': bool(rights.can_reply),
        'can_read_messages': bool(rights.can_read_messages),
        'can_delete_sent_messages': bool(rights.can_delete_sent_messages),
        'can_delete_all_messages': bool(rights.can_delete_all_messages),
    }


def get_missing_rights(connection: BusinessConnection) -> list[str]:
    """Get list of missing business rights names."""
    rights = _extract_rights(connection.rights)
    return [name for name, is_granted in rights.items() if not is_granted]


def save_connection(database: Database, connection: BusinessConnection) -> None:
    """Save business connection data to database."""
    rights = _extract_rights(connection.rights)

    connection_data = BusinessConnectionData(
        connection_id=connection.id,
        user_id=connection.user.id,
        user_chat_id=connection.user_chat_id,
        is_enabled=connection.is_enabled,
        can_reply=rights['can_reply'],
        can_read_messages=rights['can_read_messages'],
        can_delete_sent_messages=rights['can_delete_sent_messages'],
        can_delete_all_messages=rights['can_delete_all_messages'],
    )
    database.business.save(connection_data)


async def get_connection(bot: Bot, connection_id: str) -> BusinessConnection | None:
    """Get business connection by ID safely."""
    try:
        return await bot.get_business_connection(
            business_connection_id=connection_id,
        )
    except Exception as get_error:
        logger.error('[BUSINESS] Connection fetch failed: {0}'.format(get_error))
        return None


async def delete_message(bot: Bot, connection_id: str, message_id: int) -> None:
    """Delete message in business connection."""
    await bot.delete_business_messages(
        business_connection_id=connection_id,
        message_ids=[message_id],
    )


def is_antispam_message(
    database: Database,
    antispam_service: AntiSpamService,
    connection_id: str,
    chat_id: int,
    sender_id: int | None,
) -> bool:
    """Check if message is spam using antispam service."""
    if sender_id is None or not database.antispam.find(connection_id):
        return False

    return antispam_service.check(connection_id, chat_id, sender_id)
