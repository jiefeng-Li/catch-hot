"""手动触发抓取 API（调试用，也便于验收测试）。"""
import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Tag
from ..platforms import resolve_platforms
from ..schemas import JobOut
from ..services.crawler import run_fetch_for_tag

router = APIRouter(prefix="/api", tags=["fetch"])


@router.post("/tags/{tag_id}/fetch", response_model=list[JobOut], status_code=202)
async def trigger_fetch(tag_id: int, db: Session = Depends(get_db)):
    """立即对指定标签执行一次全平台抓取，返回各平台 Job 记录。"""
    tag = db.get(Tag, tag_id)
    if tag is None or tag.deleted:
        raise HTTPException(status_code=404, detail="标签不存在")
    platforms = resolve_platforms(tag.platforms)
    if not platforms:
        raise HTTPException(status_code=422, detail="无可用平台")
    jobs = await asyncio.gather(*(run_fetch_for_tag(db, tag, p) for p in platforms))
    return [JobOut.model_validate(j) for j in jobs]
