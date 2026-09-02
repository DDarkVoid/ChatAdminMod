import sqlite3
from pathlib import Path
from typing import Any, Optional


class Database:
    def __init__(self, database_path: str = "secretar.db") -> None:
        self.database_path = database_path
        path = Path(database_path)
        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.create_tables()
        self.migrate_tables()

    def create_tables(self) -> None:
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS mutes (
                connection_id TEXT NOT NULL,
                chat_id INTEGER NOT NULL,
                mute_until INTEGER DEFAULT NULL,
                PRIMARY KEY (connection_id, chat_id)
            )
        """)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT NOT NULL DEFAULT 'ru'
            )
        """)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS antispam (
                connection_id TEXT PRIMARY KEY,
                enabled INTEGER NOT NULL DEFAULT 0
            )
        """)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS business_connections (
                connection_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                user_chat_id INTEGER NOT NULL,
                is_enabled INTEGER NOT NULL DEFAULT 1,
                can_reply INTEGER NOT NULL DEFAULT 0,
                can_read_messages INTEGER NOT NULL DEFAULT 0,
                can_delete_sent_messages INTEGER NOT NULL DEFAULT 0,
                can_delete_all_messages INTEGER NOT NULL DEFAULT 0
            )
        """)
        self.connection.commit()

    def migrate_tables(self) -> None:
        self._add_column_if_missing("business_connections", "user_chat_id", "INTEGER NOT NULL DEFAULT 0")
        self._add_column_if_missing("business_connections", "is_enabled", "INTEGER NOT NULL DEFAULT 1")
        self._add_column_if_missing("business_connections", "can_reply", "INTEGER NOT NULL DEFAULT 0")
        self._add_column_if_missing("business_connections", "can_read_messages", "INTEGER NOT NULL DEFAULT 0")
        self._add_column_if_missing("business_connections", "can_delete_sent_messages", "INTEGER NOT NULL DEFAULT 0")
        self._add_column_if_missing("business_connections", "can_delete_all_messages", "INTEGER NOT NULL DEFAULT 0")
        self.connection.commit()

    def _add_column_if_missing(self, table_name: str, column_name: str, column_definition: str) -> None:
        cursor = self.connection.execute(f"PRAGMA table_info({table_name})")
        columns = {row["name"] for row in cursor.fetchall()}
        if column_name in columns:
            return
        self.connection.execute(f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {column_definition}
        """)
        print(f"[DATABASE] Добавлен столбец {table_name}.{column_name}")

    def set_mute(self, connection_id: str, chat_id: int, mute_until: Optional[int]) -> None:
        self.connection.execute(
            """
            INSERT INTO mutes (connection_id, chat_id, mute_until)
            VALUES (?, ?, ?)
            ON CONFLICT (connection_id, chat_id)
            DO UPDATE SET mute_until = excluded.mute_until
            """,
            (connection_id, chat_id, mute_until),
        )
        self.connection.commit()

    def remove_mute(self, connection_id: str, chat_id: int) -> None:
        self.connection.execute(
            """
            DELETE FROM mutes
            WHERE connection_id = ? AND chat_id = ?
            """,
            (connection_id, chat_id),
        )
        self.connection.commit()

    def get_mute(self, connection_id: str, chat_id: int) -> Optional[int]:
        cursor = self.connection.execute(
            """
            SELECT mute_until
            FROM mutes
            WHERE connection_id = ? AND chat_id = ?
            """,
            (connection_id, chat_id),
        )
        result = cursor.fetchone()
        return result["mute_until"] if result is not None else None

    def is_muted(self, connection_id: str, chat_id: int) -> bool:
        cursor = self.connection.execute(
            """
            SELECT 1
            FROM mutes
            WHERE connection_id = ? AND chat_id = ?
            """,
            (connection_id, chat_id),
        )
        return cursor.fetchone() is not None

    def set_language(self, user_id: int, language: str) -> None:
        if language not in ("ru", "en"):
            raise ValueError("Unsupported language")
        self.connection.execute(
            """
            INSERT INTO users (user_id, language)
            VALUES (?, ?)
            ON CONFLICT (user_id)
            DO UPDATE SET language = excluded.language
            """,
            (user_id, language),
        )
        self.connection.commit()

    def get_language(self, user_id: int) -> str:
        cursor = self.connection.execute(
            """
            SELECT language
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )
        result = cursor.fetchone()
        return result["language"] if result is not None else "ru"

    def set_antispam(self, connection_id: str, enabled: bool) -> None:
        self.connection.execute(
            """
            INSERT INTO antispam (connection_id, enabled)
            VALUES (?, ?)
            ON CONFLICT (connection_id)
            DO UPDATE SET enabled = excluded.enabled
            """,
            (connection_id, int(enabled)),
        )
        self.connection.commit()

    def is_antispam_enabled(self, connection_id: str) -> bool:
        cursor = self.connection.execute(
            """
            SELECT enabled
            FROM antispam
            WHERE connection_id = ?
            """,
            (connection_id,),
        )
        result = cursor.fetchone()
        return bool(result["enabled"]) if result is not None else False

    def save_business_connection(
        self,
        connection_id: str,
        user_id: int,
        user_chat_id: int,
        is_enabled: bool,
        can_reply: bool,
        can_read_messages: bool,
        can_delete_sent_messages: bool,
        can_delete_all_messages: bool,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO business_connections (
                connection_id, user_id, user_chat_id, is_enabled,
                can_reply, can_read_messages, can_delete_sent_messages,
                can_delete_all_messages
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (connection_id)
            DO UPDATE SET
                user_id = excluded.user_id,
                user_chat_id = excluded.user_chat_id,
                is_enabled = excluded.is_enabled,
                can_reply = excluded.can_reply,
                can_read_messages = excluded.can_read_messages,
                can_delete_sent_messages = excluded.can_delete_sent_messages,
                can_delete_all_messages = excluded.can_delete_all_messages
            """,
            (
                connection_id,
                user_id,
                user_chat_id,
                int(is_enabled),
                int(can_reply),
                int(can_read_messages),
                int(can_delete_sent_messages),
                int(can_delete_all_messages),
            ),
        )
        self.connection.commit()

    def get_business_connection(self, connection_id: str) -> Optional[dict[str, Any]]:
        cursor = self.connection.execute(
            """
            SELECT *
            FROM business_connections
            WHERE connection_id = ?
            """,
            (connection_id,),
        )
        result = cursor.fetchone()
        return dict(result) if result is not None else None

    def close(self) -> None:
        self.connection.close()