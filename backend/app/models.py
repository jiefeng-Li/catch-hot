"""ORM 模型定义：对应需求 9.1 的核心实体。"""
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Tag(Base):
    """标签：用户配置的监控关键词。"""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    keyword: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    keywords: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    # 平台范围，JSON 数组，如 ["zhihu", "bilibili"]；为空表示全部已注册平台
    platforms: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # 抓取频率（分钟）
    interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    # 启停状态：False 时不再触发抓取（需求 7.1）
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # 逻辑删除（需求 7.1：删除保留历史数据）
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    jobs: Mapped[list["Job"]] = relationship(back_populates="tag")


class Job(Base):
    """抓取任务执行记录：每次标签在某平台的抓取均产生一条记录（需求 7.6）。"""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    # 状态：running / success / failed
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running", index=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_fetched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_saved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    tag: Mapped[Tag] = relationship(back_populates="jobs")


class HotItem(Base):
    """热点内容：标准化后的跨平台内容（需求 7.3 字段标准化）。"""

    __tablename__ = "hot_items"
    # 同一标签下去重指纹唯一：保证相同链接仅保留 1 条（需求 7.3 验收）
    __table_args__ = (UniqueConstraint("tag_id", "fingerprint", name="uq_tag_fingerprint"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 平台原始发布时间（可能为空）
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # 归一化热度分值 [0, 100]
    hot_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, index=True)
    # 复合多维评分（综合权威/粉丝/热度/发布时间/浏览量等），范围 [0,100]
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, index=True)
    # 原始额外元数据（平台返回的作者/浏览量等），用于审计与展示
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # 去重指纹：规范化链接的 SHA1
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False, index=True)
