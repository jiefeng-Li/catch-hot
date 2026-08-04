"""pytest 公共夹具：内存 SQLite + FastAPI TestClient（不启动真实调度器）。"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from sqlalchemy import text

from backend.app.database import Base, get_db
from backend.app.main import app


@pytest.fixture()
def db_session():
    """每个测试独立的内存数据库。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        has_keywords = conn.execute(
            text("SELECT COUNT(*) FROM pragma_table_info('tags') WHERE name = 'keywords'")
        ).scalar_one()
        if has_keywords == 0:
            conn.execute(text("ALTER TABLE tags ADD COLUMN keywords JSON"))
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session, monkeypatch):
    """TestClient，覆盖 DB 依赖并禁用调度器与 lifespan。"""
    # 防止测试触碰真实调度器
    monkeypatch.setattr("backend.app.routers.tags.scheduler_service", _DummyScheduler())

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


class _DummyScheduler:
    def sync_tag(self, *args, **kwargs):
        pass

    def remove_tag(self, *args, **kwargs):
        pass
