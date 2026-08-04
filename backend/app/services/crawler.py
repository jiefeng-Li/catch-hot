"""抓取服务：执行单标签×单平台的抓取、清洗、去重、入库。

职责边界：
- 平台调用由 platforms 适配层完成
- 失败重试（指数退避，需求 7.2 验收：失败后自动重试至少 2 次）
- 去重：链接指纹（主）+ 标题相似度（辅）（需求 7.3）
- 每个平台独立 Job 记录，单平台失败不影响其他平台（需求 7.2/7.6）
"""
import asyncio
import difflib
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import FETCH_MAX_RETRIES, TITLE_SIMILARITY_THRESHOLD
from ..models import HotItem, Job, Tag
from ..platforms import BasePlatform, make_fingerprint

logger = logging.getLogger(__name__)


async def _fetch_with_retry(platform: BasePlatform, keyword: str) -> tuple[list, int]:
    """带重试的抓取。返回 (items, retry_count)。全部失败后抛异常。"""
    last_exc: Exception | None = None
    for attempt in range(FETCH_MAX_RETRIES + 1):
        try:
            items = await platform.fetch(keyword)
            return items, attempt
        except Exception as exc:  # noqa: BLE001 需要兜底记录
            last_exc = exc
            logger.warning(
                "平台 %s 抓取失败（第 %d 次）: %s", platform.name, attempt + 1, exc
            )
            if attempt < FETCH_MAX_RETRIES:
                await asyncio.sleep(min(2 ** attempt, 8))  # 指数退避
    raise last_exc  # type: ignore[misc]


def _is_title_dup(title: str, existing_titles: list[str]) -> bool:
    """标题相似度去重（辅助策略）。"""
    for existing in existing_titles:
        if difflib.SequenceMatcher(None, title, existing).ratio() >= TITLE_SIMILARITY_THRESHOLD:
            return True
    return False


def save_items(db: Session, tag: Tag, platform_name: str, raw_items: list) -> tuple[int, int]:
    """清洗、归一化、去重并入库。返回 (fetched, saved)。"""
    all_raw_hot = [it.raw_hot for it in raw_items]

    # 本标签下已有指纹与标题（用于批次内+批次间去重）
    existing = db.execute(
        select(HotItem.fingerprint, HotItem.title).where(HotItem.tag_id == tag.id)
    ).all()
    existing_fps = {row[0] for row in existing}
    existing_titles = [row[1] for row in existing]

    saved = 0
    for raw in raw_items:
        fp = make_fingerprint(raw.url)
        if fp in existing_fps:
            continue
        if _is_title_dup(raw.title, existing_titles):
            continue
        # 平台适配器负责热度归一化
        platform = _get_platform_instance(platform_name)
        hot_score = platform.normalize_hot(raw.raw_hot, all_raw_hot) if platform else 0.0
        # 计算复合评分（多维度）：authority, followers, recency, views, hot_score
        composite_score = _compute_composite_score(raw, hot_score)

        db.add(
                HotItem(
                tag_id=tag.id,
                platform=platform_name,
                title=raw.title[:500],
                url=raw.url,
                summary=raw.summary,
                published_at=raw.published_at,
                    hot_score=hot_score,
                    score=composite_score,
                    meta=raw.extra or None,
                fingerprint=fp,
                fetched_at=datetime.now(timezone.utc),
            )
        )
        existing_fps.add(fp)
        existing_titles.append(raw.title)
        saved += 1
    return len(raw_items), saved


def _compute_composite_score(raw: object, hot_score: float) -> float:
    """基于多维度的复合评分函数，输出范围在 0-100。权重可调整。

    使用维度：
    - authority: 来源/博主权威度（0-100） -> 优先级高
    - followers: 博主粉丝数（log 缩放到 0-100）
    - recency: 发布时间距现在（越近得分越高）
    - views: 浏览量（log 缩放到 0-100）
    - hot_score: 归一化热度（0-100）

    raw.extra 字段中若包含 `author`, `followers`, `views`, `authority` 等则会被使用。
    """
    from math import log10

    # 权重配置（可调整）
    W_AUTH = 0.35
    W_FOLLOW = 0.20
    W_RECENT = 0.20
    W_VIEWS = 0.10
    W_HOT = 0.15

    # 默认值
    authority = 0.0
    followers = 0
    views = 0

    extra = getattr(raw, "extra", {}) or {}
    # authority 可以是平台给出的可信度分或来源类型（如媒体/机构）映射
    authority = float(extra.get("authority", 0) or 0)
    # followers 可能为字符串数字，尝试解析
    try:
        followers = int(extra.get("followers") or 0)
    except Exception:
        followers = 0
    try:
        views = int(extra.get("views") or 0)
    except Exception:
        views = 0

    # followers 和 views 采用 log10 缩放到 0-100
    def _log_scale(x: int, max_scale: float = 100.0) -> float:
        if x <= 0:
            return 0.0
        return min(max_scale, log10(x) / 6 * max_scale)  # 10^6 -> 100

    followers_score = _log_scale(followers)
    views_score = _log_scale(views)

    # recency：如果没有 published_at，则视为中等值 50
    recency_score = 50.0
    try:
        if raw.published_at:
            from datetime import datetime, timezone

            now = datetime.now(timezone.utc)
            delta = now - raw.published_at
            hours = delta.total_seconds() / 3600
            # 0小时 -> 100，24小时 -> 80，7天 -> 50，30天 -> 20，>90天 -> 0
            if hours <= 1:
                recency_score = 100.0
            elif hours <= 24:
                recency_score = 80.0
            elif hours <= 24 * 7:
                recency_score = 50.0
            elif hours <= 24 * 30:
                recency_score = 20.0
            else:
                recency_score = 0.0
    except Exception:
        recency_score = 50.0

    # 合并得分
    final = (
        authority * W_AUTH
        + followers_score * W_FOLLOW
        + recency_score * W_RECENT
        + views_score * W_VIEWS
        + float(hot_score or 0) * W_HOT
    )
    # 保证 0-100
    try:
        final = max(0.0, min(100.0, round(final, 2)))
    except Exception:
        final = 0.0
    return final


def _get_platform_instance(name: str) -> BasePlatform | None:
    from ..platforms import get_platform

    return get_platform(name)


async def run_fetch_for_tag(db: Session, tag: Tag, platform: BasePlatform) -> Job:
    """执行一次 标签×平台 抓取，并落库 Job 记录（成功/失败均有记录）。"""
    job = Job(tag_id=tag.id, platform=platform.name, status="running")
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        keywords = tag.keywords or []
        if not keywords and tag.keyword:
            keywords = [tag.keyword]
        if not keywords:
            raise ValueError("标签缺少可抓取关键词")

        all_raw_items: list = []
        for keyword in keywords:
            raw_items, retry_count = await _fetch_with_retry(platform, keyword)
            all_raw_items.extend(raw_items)

        fetched, saved = save_items(db, tag, platform.name, all_raw_items)
        job.status = "success"
        job.retry_count = 0
        job.items_fetched = fetched
        job.items_saved = saved
    except Exception as exc:  # noqa: BLE001 单平台失败不影响其他平台
        logger.error("标签[%s] 平台[%s] 抓取最终失败: %s", tag.name, platform.name, exc)
        job.status = "failed"
        job.retry_count = FETCH_MAX_RETRIES
        job.error_message = f"{type(exc).__name__}: {exc}"[:1000]
    finally:
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
    return job
