from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "lex_ai.db"
load_dotenv(PROJECT_ROOT / ".env")

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None
_configured_url: str | None = None
_schema_initialized = False


def _database_url() -> str:
    configured = os.getenv("DATABASE_URL", "").strip()
    if configured.startswith("postgres://"):
        return configured.replace("postgres://", "postgresql+psycopg2://", 1)
    if configured:
        return configured
    return f"sqlite:///{DEFAULT_DATABASE_PATH}"


def configure_database(url: str | None = None) -> None:
    """Permite selecionar outro banco, principalmente em testes."""
    global _engine, _session_factory, _configured_url, _schema_initialized

    if _engine is not None:
        _engine.dispose()

    _engine = None
    _session_factory = None
    _configured_url = url
    _schema_initialized = False


def get_engine() -> Engine:
    global _engine, _session_factory

    if _engine is not None:
        return _engine

    url = _configured_url or _database_url()
    connect_args: dict[str, object] = {}

    if url.startswith("sqlite"):
        database_path = url.removeprefix("sqlite:///")
        if database_path and database_path != ":memory:":
            Path(database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)
        connect_args["check_same_thread"] = False
        connect_args["timeout"] = 30

    _engine = create_engine(
        url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )
    if url.startswith("sqlite"):
        @event.listens_for(_engine, "connect")
        def _configure_sqlite(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=30000")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    _session_factory = sessionmaker(
        bind=_engine,
        autoflush=False,
        expire_on_commit=False,
    )
    return _engine


def init_database() -> None:
    global _schema_initialized

    if _schema_initialized:
        return

    from database.models import Base

    Base.metadata.create_all(get_engine())
    _schema_initialized = True


def get_session() -> Session:
    init_database()
    if _session_factory is None:
        get_engine()
    assert _session_factory is not None
    return _session_factory()


@contextmanager
def session_scope() -> Iterator[Session]:
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
