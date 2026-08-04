"""任务调度器：基于 APScheduler 3.x AsyncIOScheduler。

- 每个启用标签注册一个 interval job（频率 = tag.interval_minutes）
- 标签增删改/启停时同步调度器（需求 7.1 验收：暂停标签不再触发抓取）
- 调度器 job 内部并发执行各平台抓取（单平台故障隔离）
"""
import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..database import SessionLocal
from ..models import Tag
from ..platforms import resolve_platforms
from .crawler import run_fetch_for_tag

logger = logging.getLogger(__name__)

_JOB_PREFIX = "tag_fetch_"


class SchedulerService:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()

    @staticmethod
    def _job_id(tag_id: int) -> str:
        return f"{_JOB_PREFIX}{tag_id}"

    def start(self) -> None:
        """启动调度器并为所有启用标签注册任务。"""
        if not self.scheduler.running:
            self.scheduler.start()
        self.reload_all()
        logger.info("调度器已启动")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("调度器已关闭")

    def reload_all(self) -> None:
        """从数据库全量同步调度任务。"""
        with SessionLocal() as db:
            tags = db.query(Tag).filter(Tag.deleted.is_(False)).all()
            for tag in tags:
                self.sync_tag(tag.id, tag.enabled, tag.interval_minutes)

    def sync_tag(self, tag_id: int, enabled: bool, interval_minutes: int) -> None:
        """同步单个标签的调度状态（新增/编辑/启停/删除后调用）。"""
        job_id = self._job_id(tag_id)
        existing = self.scheduler.get_job(job_id)
        if not enabled:
            if existing:
                self.scheduler.remove_job(job_id)
                logger.info("已移除调度任务: %s（标签停用或删除）", job_id)
            return
        trigger = IntervalTrigger(minutes=interval_minutes)
        if existing:
            existing.reschedule(trigger)
            logger.info("已更新调度任务: %s -> 每 %d 分钟", job_id, interval_minutes)
        else:
            self.scheduler.add_job(
                run_scheduled_fetch,
                trigger=trigger,
                args=[tag_id],
                id=job_id,
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
            logger.info("已注册调度任务: %s -> 每 %d 分钟", job_id, interval_minutes)

    def remove_tag(self, tag_id: int) -> None:
        job_id = self._job_id(tag_id)
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)


# 模块级单例，供 API 层使用
scheduler_service = SchedulerService()


async def run_scheduled_fetch(tag_id: int) -> None:
    """调度入口：加载标签并并发抓取其配置的所有平台。"""
    with SessionLocal() as db:
        tag = db.get(Tag, tag_id)
        if tag is None or tag.deleted or not tag.enabled:
            return
        platforms = resolve_platforms(tag.platforms)
        if not platforms:
            logger.warning("标签[%s] 无可用平台，跳过", tag.name)
            return
        # 并发执行，单平台异常已被 run_fetch_for_tag 捕获隔离
        await asyncio.gather(*(run_fetch_for_tag(db, tag, p) for p in platforms))
