"""Owner command handling."""

import logging
import time
from collections.abc import Awaitable, Callable

from aiogram import Bot
from aiogram.types import Message

from app.database.database import Database
from app.handlers.business_helpers import delete_command
from app.services.mute_service import MuteService

logger = logging.getLogger(__name__)

CommandHandler = Callable[[Message, str, int, Bot], Awaitable[None]]


def _format_time(minutes: int, seconds: int) -> str:
    """Format time string."""
    if minutes:
        return '{0} min {1} sec'.format(minutes, seconds)
    return '{0} sec'.format(seconds)


def _mute_response(
    database: Database,
    connection_id: str,
    chat_id: int,
    mute_until: int | None,
) -> str:
    """Build mute status response."""
    if mute_until is None:
        if database.mutes.exists(connection_id, chat_id):
            return '🔇 Chat is muted permanently.'
        return '🔊 Chat is not muted.'

    remaining = mute_until - int(time.time())
    if remaining <= 0:
        database.mutes.remove(connection_id, chat_id)
        return '🔊 Mute has already expired.'

    minutes, seconds = divmod(remaining, 60)
    time_text = _format_time(minutes, seconds)
    return '🔇 Chat is muted.\n⏱ Time remaining: {0}'.format(time_text)


async def _send_business_text(message: Message, text: str) -> None:
    """Send reply in business chat."""
    try:
        await message.answer(text)
    except Exception as send_error:
        logger.error(
            '[BUSINESS] Failed to send reply: {0}'.format(send_error),
        )


class BusinessCommandHandler(object):
    """Owner command handler."""

    def __init__(
        self,
        database: Database,
        mute_service: MuteService,
    ) -> None:
        """Initialize handler."""
        self._database = database
        self._mute_service = mute_service
        self._handlers: dict[str, CommandHandler] = {
            '.unmute': self._unmute,
            '.mutestatus': self._mutestatus,
            '.antispam': self._toggle_antispam,
        }

    async def process(self, message: Message, bot: Bot) -> bool:
        """Process command from message."""
        if not message.text or message.business_connection_id is None:
            return False

        return await self._execute_command(message, bot)

    async def _execute_command(
        self,
        message: Message,
        bot: Bot,
    ) -> bool:
        """Execute recognized command."""
        conn_id = message.business_connection_id
        if conn_id is None:
            return False

        cmd = (message.text or '').strip().lower()
        chat_id = message.chat.id

        cmd_handler = self._handlers.get(cmd)
        if cmd_handler is not None:
            await cmd_handler(message, conn_id, chat_id, bot)
            return True

        if cmd.startswith('.mute'):
            await self._handle_mute(message, conn_id, cmd, bot)
            return True

        return False

    async def _handle_mute(
        self,
        message: Message,
        conn_id: str,
        cmd: str,
        bot: Bot,
    ) -> None:
        """Process mute command with optional duration."""
        chat_id = message.chat.id
        duration = cmd[5:].strip() if cmd.startswith('.mute ') else None

        if not duration:
            self._mute_service.mute(conn_id, chat_id)
            logger.info('[MUTE] CHAT {0} muted forever'.format(chat_id))
            await delete_command(bot, conn_id, message.message_id)
            return

        try:
            self._mute_service.mute(conn_id, chat_id, duration)
        except ValueError as mute_error:
            logger.error('[MUTE] {0}'.format(mute_error))
            await delete_command(bot, conn_id, message.message_id)
            return

        logger.info(
            '[MUTE] CHAT {0} muted for {1}'.format(chat_id, duration),
        )
        await delete_command(bot, conn_id, message.message_id)

    async def _unmute(
        self,
        message: Message,
        connection_id: str,
        chat_id: int,
        bot: Bot,
    ) -> None:
        """Remove mute."""
        self._mute_service.unmute(connection_id, chat_id)
        logger.info('[MUTE] CHAT {0} unmuted'.format(chat_id))
        await delete_command(bot, connection_id, message.message_id)

    async def _mutestatus(
        self,
        message: Message,
        connection_id: str,
        chat_id: int,
        bot: Bot,
    ) -> None:
        """Show mute status."""
        mute_until = self._database.mutes.find(connection_id, chat_id)
        response_text = _mute_response(
            self._database,
            connection_id,
            chat_id,
            mute_until,
        )
        await _send_business_text(message, response_text)
        await delete_command(bot, connection_id, message.message_id)

    async def _toggle_antispam(
        self,
        message: Message,
        connection_id: str,
        chat_id: int,
        bot: Bot,
    ) -> None:
        """Toggle antispam."""
        old_state = self._database.antispam.find(connection_id) or False
        self._database.antispam.save(connection_id, not old_state)

        text = (
            'Antispam disabled.'
            if old_state
            else 'Antispam enabled.\nThreshold: 10 msgs / 5 sec.\nMute: 30 sec.'
        )
        await _send_business_text(message, text)
        await delete_command(bot, connection_id, message.message_id)
