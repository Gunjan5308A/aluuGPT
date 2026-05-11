import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator
from uuid import uuid4

from dotenv import load_dotenv

from .security import generate_session_token

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/chat_history.db")
USE_SQLITE = not DATABASE_URL

# Ensure data directory exists for SQLite
if USE_SQLITE:
    os.makedirs(os.path.dirname(DATABASE_PATH) or ".", exist_ok=True)


def _utc_iso(hours: int = 0, days: int = 0) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours, days=days)).isoformat()


class SQLiteDict(dict):
    """Wrapper to make sqlite3.Row behave like a dict"""
    def __init__(self, keys, values):
        super().__init__(zip(keys, values))


@contextmanager
def get_connection() -> Iterator[Any]:
    if USE_SQLITE:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError(
                "psycopg is required when DATABASE_URL is set. Add psycopg[binary] to requirements."
            ) from exc

        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def _row_to_dict(row: Any) -> dict | None:
    if row is None:
        return None
    if USE_SQLITE and isinstance(row, sqlite3.Row):
        return dict(row)
    return dict(row)


_schema_initialized = False


def ensure_schema() -> None:
    global _schema_initialized
    if _schema_initialized:
        return
    
    try:
        if USE_SQLITE:
            _ensure_sqlite_schema()
        else:
            _ensure_postgres_schema()
        _schema_initialized = True
    except Exception as e:
        print(f"Warning: Could not initialize database schema: {e}")
        _schema_initialized = True  # Mark as initialized to avoid repeated attempts


def _ensure_sqlite_schema() -> None:
    users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """
    sessions_sql = """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """
    history_sql = """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """

    with get_connection() as conn:
        conn.execute(users_sql)
        conn.execute(sessions_sql)
        conn.execute(history_sql)


def _ensure_postgres_schema() -> None:
    users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """
    sessions_sql = """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMPTZ NOT NULL
        )
    """
    history_sql = """
        CREATE TABLE IF NOT EXISTS history (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """

    with get_connection() as conn:
        conn.execute(users_sql)
        conn.execute(sessions_sql)
        conn.execute(history_sql)
        columns = {
            row["name"]
            for row in conn.execute(
                "SELECT column_name AS name FROM information_schema.columns WHERE table_name = 'users'"
            ).fetchall()
        }
        if "username" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT")
        if "email" in columns:
            conn.execute(
                "UPDATE users SET username = COALESCE(username, email) WHERE username IS NULL"
            )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS users_username_unique ON users (username)"
        )


def normalize_username(username: str) -> str:
    return username.strip().lower()


def get_user_by_username(username: str) -> dict | None:
    ensure_schema()
    with get_connection() as conn:
        if USE_SQLITE:
            row = conn.execute(
                "SELECT id, username, password_hash, password_salt, created_at FROM users WHERE username = ?",
                (normalize_username(username),),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id, username, password_hash, password_salt, created_at FROM users WHERE username = %s",
                (normalize_username(username),),
            ).fetchone()
        return _row_to_dict(row)


def get_user_by_id(user_id: str) -> dict | None:
    ensure_schema()
    with get_connection() as conn:
        if USE_SQLITE:
            row = conn.execute(
                "SELECT id, username, password_hash, password_salt, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id, username, password_hash, password_salt, created_at FROM users WHERE id = %s",
                (user_id,),
            ).fetchone()
        return _row_to_dict(row)


def create_user(username: str, password_hash: str, password_salt: str) -> dict:
    ensure_schema()
    normalized_username = normalize_username(username)
    user = {
        "id": uuid4().hex,
        "username": normalized_username,
        "password_hash": password_hash,
        "password_salt": password_salt,
    }
    with get_connection() as conn:
        if USE_SQLITE:
            conn.execute(
                "INSERT INTO users (id, username, password_hash, password_salt) VALUES (?, ?, ?, ?)",
                (user["id"], user["username"], user["password_hash"], user["password_salt"]),
            )
        else:
            conn.execute(
                """
                INSERT INTO users (id, username, password_hash, password_salt)
                VALUES (%s, %s, %s, %s)
                """,
                (user["id"], user["username"], user["password_hash"], user["password_salt"]),
            )
    return user


def create_session(user_id: str, days_valid: int = 14) -> dict:
    ensure_schema()
    token = generate_session_token()
    expires_at = _utc_iso(days=days_valid)
    with get_connection() as conn:
        if USE_SQLITE:
            conn.execute(
                "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
                (token, user_id, expires_at),
            )
        else:
            conn.execute(
                "INSERT INTO sessions (token, user_id, expires_at) VALUES (%s, %s, %s)",
                (token, user_id, expires_at),
            )
    return {"token": token, "expires_at": expires_at}


def get_session(token: str) -> dict | None:
    ensure_schema()
    with get_connection() as conn:
        if USE_SQLITE:
            row = conn.execute(
                "SELECT token, user_id, created_at, expires_at FROM sessions WHERE token = ? AND expires_at > datetime('now')",
                (token,),
            ).fetchone()
        else:
            row = conn.execute(
                """
                SELECT token, user_id, created_at, expires_at
                FROM sessions
                WHERE token = %s AND expires_at > NOW()
                """,
                (token,),
            ).fetchone()
        return _row_to_dict(row)


def delete_session(token: str) -> None:
    ensure_schema()
    with get_connection() as conn:
        if USE_SQLITE:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        else:
            conn.execute("DELETE FROM sessions WHERE token = %s", (token,))


def add_history(user_id: str, role: str, content: str) -> None:
    ensure_schema()
    with get_connection() as conn:
        if USE_SQLITE:
            conn.execute(
                "INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content),
            )
        else:
            conn.execute(
                "INSERT INTO history (user_id, role, content) VALUES (%s, %s, %s)",
                (user_id, role, content),
            )


def get_history(user_id: str, limit: int = 5) -> list[dict]:
    ensure_schema()
    with get_connection() as conn:
        if USE_SQLITE:
            rows = conn.execute(
                "SELECT role, content, created_at FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM history
                WHERE user_id = %s
                ORDER BY id DESC
                LIMIT %s
                """,
                (user_id, limit),
            ).fetchall()
    return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]
