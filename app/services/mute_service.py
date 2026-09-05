"""Mute service."""

import time
from typing import Optional

from app.database.database import Database
from app.utils.time_parser import TimeParser


class MuteService(object):
    """Mute management service."""

    def __init__(self, database: Database) -> None:
        """Initialize with database instance."""
        self._database = database

    def mute(
        self,
        connection_id: str,
        chat_id: int,
        duration: Optional[str] = None,
    ) -> Optional[int]:
        """Set mute."""
        if duration is None:
            mute_until = None
        else:
            mute_until = int(time.time()) + TimeParser.parse(duration)
        self._database.mutes.save(connection_id, chat_id, mute_until)
        return mute_until

    def unmute(self, connection_id: str, chat_id: int) -> None:
        """Remove mute."""
        self._database.mutes.remove(connection_id, chat_id)

    def is_muted(self, connection_id: str, chat_id: int) -> bool:
        """Check if active mute exists."""
        if not self._database.mutes.exists(connection_id, chat_id):
            return False
        mute_until = self._database.mutes.find(connection_id, chat_id)
        if mute_until is None:
            return True
        if mute_until > int(time.time()):
            return True
        self._database.mutes.remove(connection_id, chat_id)
        return False

    def get_mute_until(self, connection_id: str, chat_id: int) -> Optional[int]:
        """Get mute end time."""
        return self._database.mutes.find(connection_id, chat_id)
