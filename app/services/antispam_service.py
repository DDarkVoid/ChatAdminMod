from typing import Dict, Tuple

class AntiSpamService:
    def __init__(self) -> None:
        self.storage: Dict[Tuple[str, int, int], int] = {}  # (connection_id, chat_id, user_id) -> last_time
        self.threshold = 10
        self.window = 5  # seconds

    def check(self, connection_id: str, chat_id: int, user_id: int) -> bool:
        key = (connection_id, chat_id, user_id)
        now = int(__import__('time').time())
        if key not in self.storage:
            self.storage[key] = now
            return False
        last = self.storage[key]
        if now - last < self.window:
            self.storage[key] = now
            # считаем количество за window, но для упрощения срабатывает сразу
            return True
        self.storage[key] = now
        return False