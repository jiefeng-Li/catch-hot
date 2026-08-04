"""热点列表与趋势分析 API（需求 7.4 / 7.5 / 7.6）。"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import HOT_ITEMS_DEFAULT_LIMIT
from ..database import get_db
from ..models import HotItem, Job, Tag
from ..schemas import HotItemList, HotItemOut, JobOut, PlatformDist, TrendPoint

router = APIRouter(prefix="/api", tags=["items"])


@router.delete("/admin/reset-data")
def reset_data(db: Session = Depends(get_db)):
    """清空热点与任务历史，便于重新抓取验证。仅开发/测试场景使用。"""
    deleted_hot = db.execute(select(HotItem)).scalars().all()
    deleted_jobs = db.execute(select(Job)).scalars().all()
    for row in deleted_hot:
        db.delete(row)
    for row in deleted_jobs:
        db.delete(row)
    db.commit()
    return {"ok": True, "hot_items_deleted": len(deleted_hot), "jobs_deleted": len(deleted_jobs)}


@router.get("/hot-items", response_model=HotItemList)
def list_hot_items(
    tag_id: int | None = None,
    platform: str | None = None,
    keyword: str | None = Query(default=None, description="标题/摘要二次筛选"),
    hours: int | None = Query(default=None, ge=1, description="最近 N 小时"),
    sort: str = Query(default="time", pattern="^(time|hot)$"),
    limit: int = Query(default=HOT_ITEMS_DEFAULT_LIMIT, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """热点列表：默认按时间返回最近 50 条（需求 7.4 验收）。"""
    stmt = select(HotItem)
    count_stmt = select(func.count(HotItem.id))

    if tag_id is not None:
        stmt = stmt.where(HotItem.tag_id == tag_id)
        count_stmt = count_stmt.where(HotItem.tag_id == tag_id)
    if platform:
        stmt = stmt.where(HotItem.platform == platform)
        count_stmt = count_stmt.where(HotItem.platform == platform)
    if keyword:
        like = f"%{keyword}%"
        cond = HotItem.title.like(like) | HotItem.summary.like(like)
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    if hours:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = stmt.where(HotItem.fetched_at >= since)
        count_stmt = count_stmt.where(HotItem.fetched_at >= since)

    order_col = HotItem.hot_score.desc() if sort == "hot" else HotItem.fetched_at.desc()
    total = db.execute(count_stmt).scalar_one()
    items = db.execute(stmt.order_by(order_col).offset(offset).limit(limit)).scalars().all()
    return HotItemList(total=total, items=[HotItemOut.model_validate(it) for it in items])


@router.get("/tags/{tag_id}/trend", response_model=list[TrendPoint])
def tag_trend(
    tag_id: int,
    days: int = Query(default=7, ge=7, le=30),
    db: Session = Depends(get_db),
):
    """标签近 7-30 天数据量与热度趋势（需求 7.5）。"""
    tag = db.get(Tag, tag_id)
    if tag is None or tag.deleted:
        raise HTTPException(status_code=404, detail="标签不存在")

    since = datetime.now(timezone.utc) - timedelta(days=days)
    date_col = func.date(HotItem.fetched_at)
    rows = db.execute(
        select(date_col.label("date"), func.count().label("count"), func.coalesce(func.sum(HotItem.hot_score), 0).label("total_hot"))
        .where(HotItem.tag_id == tag_id, HotItem.fetched_at >= since)
        .group_by(date_col)
        .order_by(date_col)
    ).all()
    return [TrendPoint(date=str(r.date), count=r.count, total_hot=round(r.total_hot, 2)) for r in rows]


@router.get("/tags/{tag_id}/platform-distribution", response_model=list[PlatformDist])
def platform_distribution(tag_id: int, db: Session = Depends(get_db)):
    """热门来源平台分布（需求 7.5）。"""
    tag = db.get(Tag, tag_id)
    if tag is None or tag.deleted:
        raise HTTPException(status_code=404, detail="标签不存在")
    rows = db.execute(
        select(HotItem.platform, func.count().label("count"))
        .where(HotItem.tag_id == tag_id)
        .group_by(HotItem.platform)
        .order_by(func.count().desc())
    ).all()
    return [PlatformDist(platform=r.platform, count=r.count) for r in rows]


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    tag_id: int | None = None,
    status: str | None = Query(default=None, pattern="^(running|success|failed)$"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """任务执行日志（需求 7.6：所有任务可追踪，失败可定位平台与错误）。"""
    stmt = select(Job)
    if tag_id is not None:
        stmt = stmt.where(Job.tag_id == tag_id)
    if status:
        stmt = stmt.where(Job.status == status)
    items = db.execute(stmt.order_by(Job.started_at.desc()).limit(limit)).scalars().all()
    return [JobOut.model_validate(j) for j in items]
