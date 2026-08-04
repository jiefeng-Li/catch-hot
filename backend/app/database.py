"""数据库引擎与会话管理。

使用 SQLAlchemy 2.x 同步引擎，默认连接 MySQL；测试可通过环境变量切换 SQLite。
"""
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATA_DIR, DATABASE_URL


class Base(DeclarativeBase):
    """所有 ORM 模型的声明式基类。"""


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite:")


DATA_DIR.mkdir(parents=True, exist_ok=True)

_engine_kwargs: dict = {"pool_pre_ping": True}
if _is_sqlite(DATABASE_URL):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)


if _is_sqlite(DATABASE_URL):

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _connection_record):
        """开启 WAL 与外键约束，提升并发读写能力（仅 SQLite）。"""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    """FastAPI 依赖：每个请求一个会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建全部数据表（幂等），并为已存在的 SQLite 数据库补充新列。"""
    from . import models  # noqa: F401 确保模型已注册到 metadata

    Base.metadata.create_all(bind=engine)

    if not _is_sqlite(DATABASE_URL):
        return

    with engine.begin() as conn:
        has_keywords = conn.execute(
            text("SELECT COUNT(*) FROM pragma_table_info('tags') WHERE name = 'keywords'")
        ).scalar_one()
        if has_keywords == 0:
            conn.execute(text("ALTER TABLE tags ADD COLUMN keywords JSON"))

        inspector = inspect(engine)
        if "hot_items" in inspector.get_table_names():
            hot_cols = {col["name"] for col in inspector.get_columns("hot_items")}
            if "score" not in hot_cols:
                conn.execute(text("ALTER TABLE hot_items ADD COLUMN score FLOAT NOT NULL DEFAULT 0.0"))
            if "meta" not in hot_cols:
                conn.execute(text("ALTER TABLE hot_items ADD COLUMN meta JSON"))
