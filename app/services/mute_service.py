import time
from typing import Optional

from app.database.database import Database
from app.utils.time_parser import TimeParser


class MuteService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def mute(self, connection_id: str, chat_id: int, duration: Optional[str] = None) -> Optional[int]:
        if duration is None:
            mute_until = None
        else:
            mute_until = int(time.time()) + TimeParser.parse(duration)
        self.database.set_mute(connection_id, chat_id, mute_until)
        return mute_until

    def unmute(self, connection_id: str, chat_id: int) -> None:
        self.database.remove_mute(connection_id, chat_id)

    def is_muted(self, connection_id: str, chat_id: int) -> bool:
        mute_until = self.database.get_mute(connection_id, chat_id)
        if mute_until is None:
            return self.database.is_muted(connection_id, chat_id)
        if mute_until > int(time.time()):
            return True
        self.database.remove_mute(connection_id, chat_id)
        return False

    def get_mute_until(self, connection_id: str, chat_id: int) -> Optional[int]:
        if not self.database.is_muted(connection_id, chat_id):
            return None
        return self.database.get_mute(connection_id, chat_id)