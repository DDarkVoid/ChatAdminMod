"""SQLite database module."""

import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Final

logger = logging.getLogger(__name__)

MUTE_SAVE_QUERY: Final[str] = """
INSERT INTO mutes (connection_id, chat_id, mute_until)
VALUES (?, ?, ?)
ON CONFLICT (connection_id, chat_id)
DO UPDATE SET mute_until = excluded.mute_until
"""

USER_SAVE_QUERY: Final[str] = """
INSERT INTO users (user_id, language)
VALUES (?, ?)
ON CONFLICT (user_id)
DO UPDATE SET language = excluded.language
"""

ANTISPAM_SAVE_QUERY: Final[str] = """
INSERT INTO antispam (connection_id, enabled)
VALUES (?, ?)
ON CONFLICT (connection_id)
DO UPDATE SET enabled = excluded.enabled
"""

BUSINESS_SAVE_QUERY: Final[str] = """
INSERT INTO business_connections (
    connection_id,
    user_id,
    user_chat_id,
    is_enabled,
    can_reply,
    can_read_messages,
    can_delete_sent_messages,
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
"""

CREATE_TABLES_QUERY: Final[str] = """
CREATE TABLE IF NOT EXISTS mutes (
    connection_id TEXT NOT NULL,
    chat_id INTEGER NOT NULL,
    mute_until INTEGER DEFAULT NULL,
    PRIMARY KEY (connection_id, chat_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    language TEXT NOT NULL DEFAULT 'ru'
);

CREATE TABLE IF NOT EXISTS antispam (
    connection_id TEXT PRIMARY KEY,
    enabled INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS business_connections (
    connection_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_chat_id INTEGER NOT NULL,
    is_enabled INTEGER NOT NULL DEFAULT 1,
    can_reply INTEGER NOT NULL DEFAULT 0,
    can_read_messages INTEGER NOT NULL DEFAULT 0,
    can_delete_sent_messages INTEGER NOT NULL DEFAULT 0,
    can_delete_all_messages INTEGER NOT NULL DEFAULT 0
);
"""

Migration = tuple[str, str]

MIGRATION_QUERIES: Final[tuple[Migration, ...]] = (
    (
        'user_chat_id',
        'ALTER TABLE business_connections ADD COLUMN user_chat_id INTEGER NOT NULL DEFAULT 0',
    ),
    (
        'is_enabled',
        'ALTER TABLE business_connections ADD COLUMN is_enabled INTEGER NOT NULL DEFAULT 1',
    ),
    (
        'can_reply',
        'ALTER TABLE business_connections ADD COLUMN can_reply INTEGER NOT NULL DEFAULT 0',
    ),
    (
        'can_read_messages',
        'ALTER TABLE business_connections ADD COLUMN can_read_messages INTEGER NOT NULL DEFAULT 0',
    ),
    (
        'can_delete_sent_messages',
        'ALTER TABLE business_connections ADD COLUMN can_delete_sent_messages INTEGER NOT NULL DEFAULT 0',
    ),
    (
        'can_delete_all_messages',
        'ALTER TABLE business_connections ADD COLUMN can_delete_all_messages INTEGER NOT NULL DEFAULT 0',
    ),
)


@dataclass
class BusinessConnectionData(object):
    """Business connection data."""

    connection_id: str
    user_id: int
    user_chat_id: int
    is_enabled: bool
    can_reply: bool
    can_read_messages: bool
    can_delete_sent_messages: bool
    can_delete_all_messages: bool


class MuteStorage(object):
    """Store and manage mute records."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize the storage."""
        self._connection = connection

    def save(
        self,
        connection_id: str,
        chat_id: int,
        mute_until: int | None,
    ) -> None:
        """Save a mute record."""
        self._connection.execute(
            MUTE_SAVE_QUERY,
            (connection_id, chat_id, mute_until),
        )
        self._connection.commit()

    def remove(self, connection_id: str, chat_id: int) -> None:
        """Remove a mute record."""
        self._connection.execute(
            'DELETE FROM mutes WHERE connection_id = ? AND chat_id = ?',
            (connection_id, chat_id),
        )
        self._connection.commit()

    def find(self, connection_id: str, chat_id: int) -> int | None:
        """Find the mute end time."""
        cursor = self._connection.execute(
            'SELECT mute_until FROM mutes WHERE connection_id = ? AND chat_id = ?',
            (connection_id, chat_id),
        )
        row = cursor.fetchone()
        return row['mute_until'] if row else None

    def exists(self, connection_id: str, chat_id: int) -> bool:
        """Check if a mute record exists."""
        cursor = self._connection.execute(
            'SELECT 1 FROM mutes WHERE connection_id = ? AND chat_id = ?',
            (connection_id, chat_id),
        )
        return cursor.fetchone() is not None


class UserStorage(object):
    """Store and manage user records."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize the storage."""
        self._connection = connection

    def save(self, user_id: int, language: str) -> None:
        """Save a user record."""
        if language not in {'ru', 'en'}:
            raise ValueError('Unsupported language')
        self._connection.execute(
            USER_SAVE_QUERY,
            (user_id, language),
        )
        self._connection.commit()

    def find(self, user_id: int) -> str | None:
        """Find a user's language."""
        cursor = self._connection.execute(
            'SELECT language FROM users WHERE user_id = ?',
            (user_id,),
        )
        row = cursor.fetchone()
        return row['language'] if row else None


class AntispamStorage(object):
    """Store and manage antispam settings."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize the storage."""
        self._connection = connection

    def save(self, connection_id: str, enabled: bool) -> None:
        """Save an antispam setting."""
        self._connection.execute(
            ANTISPAM_SAVE_QUERY,
            (connection_id, int(enabled)),
        )
        self._connection.commit()

    def find(self, connection_id: str) -> bool | None:
        """Find an antispam setting."""
        cursor = self._connection.execute(
            'SELECT enabled FROM antispam WHERE connection_id = ?',
            (connection_id,),
        )
        row = cursor.fetchone()
        return bool(row['enabled']) if row else None


class BusinessStorage(object):
    """Store and manage business connections."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize the storage."""
        self._connection = connection

    def save(self, business_data: BusinessConnectionData) -> None:
        """Save a business connection."""
        record = (
            business_data.connection_id,
            business_data.user_id,
            business_data.user_chat_id,
            int(business_data.is_enabled),
            int(business_data.can_reply),
            int(business_data.can_read_messages),
            int(business_data.can_delete_sent_messages),
            int(business_data.can_delete_all_messages),
        )
        self._connection.execute(BUSINESS_SAVE_QUERY, record)
        self._connection.commit()

    def find(self, connection_id: str) -> dict[str, object] | None:
        """Find a business connection."""
        cursor = self._connection.execute(
            'SELECT * FROM business_connections WHERE connection_id = ?',
            (connection_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


class Database(object):
    """Main database interface."""

    def __init__(self, database_path: str = 'secretar.db') -> None:
        """Initialize the database."""
        self._path = Path(database_path)
        if self._path.parent != Path('.'):
            self._path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(
            database_path,
            check_same_thread=False,
        )
        self._connection.row_factory = sqlite3.Row
        self._create_tables()
        self._migrate_tables()

        self.mutes = MuteStorage(self._connection)
        self.users = UserStorage(self._connection)
        self.antispam = AntispamStorage(self._connection)
        self.business = BusinessStorage(self._connection)

    def close(self) -> None:
        """Close the database connection."""
        self._connection.close()

    def _create_tables(self) -> None:
        """Create all tables."""
        self._connection.executescript(CREATE_TABLES_QUERY)
        self._connection.commit()

    def _migrate_tables(self) -> None:
        """Apply table migrations."""
        existing = self._get_business_columns()
        for column_name, query in MIGRATION_QUERIES:
            if column_name not in existing:
                self._connection.execute(query)
        self._connection.commit()

    def _get_business_columns(self) -> set[str]:
        """Get column names of the business_connections table."""
        cursor = self._connection.execute(
            'PRAGMA table_info(business_connections)',
        )
        return {row['name'] for row in cursor.fetchall()}
