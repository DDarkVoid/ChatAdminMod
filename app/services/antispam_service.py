"""Antispam service module."""

import time
from collections import deque
from typing import Final

DEFAULT_THRESHOLD: Final[int] = 10
DEFAULT_WINDOW: Final[int] = 5


class AntiSpamService(object):
    """Message frequency checker."""

    def __init__(
        self,
        threshold: int = DEFAULT_THRESHOLD,
        window: int = DEFAULT_WINDOW,
    ) -> None:
        """Initialize antispam settings."""
        self.storage: dict[tuple[str, int, int], deque[int]] = {}
        self.threshold = threshold
        self.window = window

    def check(self, connection_id: str, chat_id: int, user_id: int) -> bool:
        """Check if message limit exceeded within the time window."""
        key = (connection_id, chat_id, user_id)
        now = int(time.time())

        if key not in self.storage:
            self.storage[key] = deque(maxlen=self.threshold)

        timestamps = self.storage[key]
        timestamps.append(now)

        while timestamps and timestamps[0] < now - self.window:
            timestamps.popleft()

        return len(timestamps) >= self.threshold
