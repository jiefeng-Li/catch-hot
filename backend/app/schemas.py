"""Pydantic 模型：API 请求/响应约束。"""
from datetime import datetime

from pydantic import BaseModel, Field

# ---------- 标签 ----------


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    keyword: str | None = Field(default=None, min_length=1, max_length=200)
    keywords: list[str] | None = None
    platforms: list[str] | None = None  # None 表示全部平台
    interval_minutes: int = Field(default=60, ge=1, le=24 * 60)
    enabled: bool = True


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    keyword: str | None = Field(default=None, min_length=1, max_length=200)
    keywords: list[str] | None = None
    platforms: list[str] | None = None
    interval_minutes: int | None = Field(default=None, ge=1, le=24 * 60)
    enabled: bool | None = None


class TagOut(BaseModel):
    id: int
    name: str
    keyword: str
    keywords: list[str] | None
    platforms: list[str] | None
    interval_minutes: int
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- 热点内容 ----------


class HotItemOut(BaseModel):
    id: int
    tag_id: int
    platform: str
    title: str
    url: str
    summary: str | None
    published_at: datetime | None
    hot_score: float
    # 复合评分（多维度，0-100）
    score: float
    # 平台原始元数据（作者/粉丝/浏览量等），仅作展示/审计
    meta: dict | None
    fetched_at: datetime

    model_config = {"from_attributes": True}


class HotItemList(BaseModel):
    total: int
    items: list[HotItemOut]


# ---------- 任务日志 ----------


class JobOut(BaseModel):
    id: int
    tag_id: int
    platform: str
    status: str
    retry_count: int
    items_fetched: int
    items_saved: int
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None

    model_config = {"from_attributes": True}


# ---------- 趋势分析 ----------


class TrendPoint(BaseModel):
    date: str  # YYYY-MM-DD
    count: int
    total_hot: float


class PlatformDist(BaseModel):
    platform: str
    count: int
