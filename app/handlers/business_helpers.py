"""Helper functions for business handlers."""

import logging

from aiogram import Bot
from aiogram.methods import DeleteBusinessMessages
from aiogram.types import BusinessConnection

from app.database.database import BusinessConnectionData, Database
from app.services.antispam_service import AntiSpamService

logger = logging.getLogger(__name__)

_RIGHTS_ATTRS = (
    ('reply', 'can_reply'),
    ('read_messages', 'can_read_messages'),
    ('delete_sent_messages', 'can_delete_sent_messages'),
    ('delete_all_messages', 'can_delete_all_messages'),
)


def get_missing_rights(connection: BusinessConnection) -> list[str]:
    """Get list of missing business rights names."""
    rights = connection.rights
    if rights is None:
        return [right_name for right_name, _ in _RIGHTS_ATTRS]

    return [
        right_name
        for right_name, attr_name in _RIGHTS_ATTRS
        if not bool(getattr(rights, attr_name, False))
    ]


def save_connection(database: Database, connection: BusinessConnection) -> None:
    """Save business connection data to database."""
    rights = connection.rights
    rights_map = {
        right_name: bool(getattr(rights, attr_name, False))
        if rights is not None
        else False
        for right_name, attr_name in _RIGHTS_ATTRS
    }

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
    """Get business connection by ID."""
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
    """Check if message triggers antispam filter."""
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
