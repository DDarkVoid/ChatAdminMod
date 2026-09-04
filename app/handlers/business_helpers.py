"""Helper functions for business handlers."""

import logging

from aiogram import Bot
from aiogram.methods import DeleteBusinessMessages
from aiogram.types import BusinessBotRights, BusinessConnection

from app.database.database import BusinessConnectionData, Database
from app.services.antispam_service import AntiSpamService

logger = logging.getLogger(__name__)


def _extract_rights(
    rights: BusinessBotRights | None,
) -> tuple[bool, bool, bool, bool]:
    """Extract business rights as boolean flags tuple."""
    if rights is None:
        return False, False, False, False
    return (
        bool(rights.can_reply),
        bool(rights.can_read_messages),
        bool(rights.can_delete_sent_messages),
        bool(rights.can_delete_all_messages),
    )


def get_missing_rights(connection: BusinessConnection) -> list[str]:
    """Get list of missing rights."""
    reply, read, del_sent, del_all = _extract_rights(connection.rights)
    missing: list[str] = []
    if not reply:
        missing.append('reply')
    if not read:
        missing.append('read_messages')
    if not del_sent:
        missing.append('delete_sent_messages')
    if not del_all:
        missing.append('delete_all_messages')
    return missing


def save_connection(database: Database, connection: BusinessConnection) -> None:
    """Save business connection data."""
    reply, read, del_sent, del_all = _extract_rights(connection.rights)
    connection_data = BusinessConnectionData(
        connection_id=connection.id,
        user_id=connection.user.id,
        user_chat_id=connection.user_chat_id,
        is_enabled=connection.is_enabled,
        can_reply=reply,
        can_read_messages=read,
        can_delete_sent_messages=del_sent,
        can_delete_all_messages=del_all,
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
