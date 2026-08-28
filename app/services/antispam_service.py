import time
from collections import defaultdict, deque


class AntiSpamService:
    LIMIT = 10
    WINDOW = 5

    def __init__(self):
        self.messages = defaultdict(deque)

    def check(
        self,
        connection_id: str,
        chat_id: int,
        user_id: int
    ) -> bool:
        key = (
            connection_id,
            chat_id,
            user_id
        )

        now = time.monotonic()

        queue = self.messages[key]

        while queue and now - queue[0] > self.WINDOW:
            queue.popleft()

        queue.append(now)

        if len(queue) >= self.LIMIT:
            queue.clear()
            return True

        return False

    def clear(
        self,
        connection_id: str,
        chat_id: int,
        user_id: int
    ):
        key = (
            connection_id,
            chat_id,
            user_id
        )

        self.messages.pop(key, None)