"""Antispam service."""

import time
from collections import deque
from typing import Dict, Tuple


class AntiSpamService(object):
    """Message frequency checker."""

    def __init__(self) -> None:
        """Initialize antispam settings."""
        self.storage: Dict[Tuple[str, int, int], deque] = {}
        self.threshold = 10
        self.window = 5

    def check(self, connection_id: str, chat_id: int, user_id: int) -> bool:
        """
        Check if message limit exceeded within the time window.

        Returns True if mute should be applied.
        """
        key = (connection_id, chat_id, user_id)
        now = int(time.time())

        if key not in self.storage:
            self.storage[key] = deque(maxlen=self.threshold)

        timestamps = self.storage[key]
        timestamps.append(now)

        while timestamps and timestamps[0] < now - self.window:
            timestamps.popleft()

        return len(timestamps) >= self.threshold
