"""标签管理 API（需求 7.1）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Tag
from ..platforms import all_platforms
from ..schemas import TagCreate, TagOut, TagUpdate
from ..services.scheduler import scheduler_service


def _normalize_keywords(keyword: str | None, keywords: list[str] | None) -> tuple[str, list[str] | None]:
    values = [item.strip() for item in (keywords or []) if item and item.strip()]
    if not values and keyword:
        values = [keyword.strip()]
    if not values:
        raise HTTPException(status_code=422, detail="至少需要提供一个关键词")
    display = ", ".join(values)
    return display, values

router = APIRouter(prefix="/api/tags", tags=["tags"])


def _validate_platforms(platforms: list[str] | None) -> None:
    if not platforms:
        return
    invalid = set(platforms) - set(all_platforms())
    if invalid:
        raise HTTPException(status_code=422, detail=f"未知平台: {sorted(invalid)}")


@router.get("", response_model=list[TagOut])
def list_tags(include_deleted: bool = False, db: Session = Depends(get_db)):
    q = db.query(Tag)
    if not include_deleted:
        q = q.filter(Tag.deleted.is_(False))
    return q.order_by(Tag.created_at.desc()).all()


@router.post("", response_model=TagOut, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    _validate_platforms(payload.platforms)
    keyword_text, keyword_list = _normalize_keywords(payload.keyword, payload.keywords)
    tag = Tag(**payload.model_dump(exclude={"keyword", "keywords"}), keyword=keyword_text, keywords=keyword_list)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    scheduler_service.sync_tag(tag.id, tag.enabled, tag.interval_minutes)
    return tag


@router.get("/{tag_id}", response_model=TagOut)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.get(Tag, tag_id)
    if tag is None or tag.deleted:
        raise HTTPException(status_code=404, detail="标签不存在")
    return tag


@router.put("/{tag_id}", response_model=TagOut)
def update_tag(tag_id: int, payload: TagUpdate, db: Session = Depends(get_db)):
    tag = db.get(Tag, tag_id)
    if tag is None or tag.deleted:
        raise HTTPException(status_code=404, detail="标签不存在")
    data = payload.model_dump(exclude_unset=True)
    if "platforms" in data:
        _validate_platforms(data["platforms"])
    if "keyword" in data or "keywords" in data:
        keyword_text, keyword_list = _normalize_keywords(data.get("keyword"), data.get("keywords"))
        tag.keyword = keyword_text
        tag.keywords = keyword_list
        data.pop("keyword", None)
        data.pop("keywords", None)
    for key, value in data.items():
        setattr(tag, key, value)
    db.commit()
    db.refresh(tag)
    scheduler_service.sync_tag(tag.id, tag.enabled, tag.interval_minutes)
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """逻辑删除：保留历史热点数据（需求 7.1）。"""
    tag = db.get(Tag, tag_id)
    if tag is None or tag.deleted:
        raise HTTPException(status_code=404, detail="标签不存在")
    tag.deleted = True
    db.commit()
    scheduler_service.remove_tag(tag_id)


@router.post("/{tag_id}/toggle", response_model=TagOut)
def toggle_tag(tag_id: int, db: Session = Depends(get_db)):
    """启停切换：暂停后不再触发抓取（需求 7.1 验收）。"""
    tag = db.get(Tag, tag_id)
    if tag is None or tag.deleted:
        raise HTTPException(status_code=404, detail="标签不存在")
    tag.enabled = not tag.enabled
    db.commit()
    db.refresh(tag)
    scheduler_service.sync_tag(tag.id, tag.enabled, tag.interval_minutes)
    return tag
