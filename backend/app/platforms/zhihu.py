"""知乎热榜适配器。

数据源：知乎热榜接口（移动端公开接口）。
关键词策略：热榜本身不含关键词搜索，MVP 阶段对标题做关键词包含过滤；
若 keyword 为空则返回全量热榜。
"""
import logging

import httpx

from ..config import FETCH_TIMEOUT
from .base import BasePlatform, RawItem, register

logger = logging.getLogger(__name__)

HOT_LIST_URL = "https://api.zhihu.com/topstory/hot-list"
SEARCH_URL = "https://www.zhihu.com/api/v4/search_v3"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    ),
    "Accept": "application/json",
}


class ZhihuPlatform(BasePlatform):
    name = "zhihu"
    display_name = "知乎热榜"

    async def fetch(self, keyword: str, limit: int = 20) -> list[RawItem]:
        # 若提供 keyword，优先尝试使用搜索接口；若搜索失败或结果为空，回退到热榜过滤策略
        items: list[RawItem] = []
        if keyword:
            try:
                async with httpx.AsyncClient(timeout=FETCH_TIMEOUT, headers=_HEADERS) as client:
                    # 搜索接口：尝试通用的 search_v3 接口，参数尽量兼容
                    resp = await client.get(SEARCH_URL, params={"q": keyword, "limit": limit})
                    resp.raise_for_status()
                    payload = resp.json()

                # payload 结构可能随接口而异，尝试多种解包方式
                results = payload.get("data") or payload.get("results") or payload.get("objects")
                if isinstance(results, dict):
                    # 有时为 { 'data': { 'items': [...] } }
                    results = results.get("items") or results.get("results") or []
                if results:
                    for obj in results:
                        # 不同结果结构有不同字段，逐级查找 title/url
                        title = None
                        url = None
                        summary = None
                        # 常见结构：obj may contain 'object' or 'target' or 'highlight'
                        candidate = obj.get("object") or obj.get("target") or obj
                        if isinstance(candidate, dict):
                            title = (candidate.get("title") or candidate.get("question_title") or candidate.get("name") or "").strip()
                            # question/object id -> 问题页
                            qid = candidate.get("id") or candidate.get("question_id")
                            if qid and not candidate.get("url"):
                                url = f"https://www.zhihu.com/question/{qid}"
                            url = url or candidate.get("url") or candidate.get("question_url")
                            summary = candidate.get("excerpt") or candidate.get("description")
                        # 兜底：文本字段
                        if not title:
                            title = (obj.get("title") or obj.get("keyword") or "").strip()
                        if not url:
                            url = obj.get("url")
                        if not title:
                            continue
                        items.append(RawItem(title=title, url=url or "", summary=summary, raw_hot=None))
                        if len(items) >= limit:
                            break
                    if items:
                        return items
            except Exception as e:  # pragma: no cover - 防外部接口不稳定
                logger.debug("zhihu search failed, fallback to hot-list: %s", e)

        # 回退到热榜接口（原有实现）
        async with httpx.AsyncClient(timeout=FETCH_TIMEOUT, headers=_HEADERS) as client:
            resp = await client.get(HOT_LIST_URL, params={"limit": max(limit * 2, 50)})
            resp.raise_for_status()
            data = resp.json()

        for entry in data.get("data", []):
            target = entry.get("target", {})
            title = (target.get("title") or "").strip()
            url = target.get("url") or ""
            # 知乎返回的是 api 跳转链接，替换为可读问题页
            qid = target.get("id")
            if qid:
                url = f"https://www.zhihu.com/question/{qid}"
            if not title or not url:
                continue
            if keyword and keyword.lower() not in title.lower():
                continue
            items.append(
                RawItem(
                    title=title,
                    url=url,
                    summary=target.get("excerpt"),
                    raw_hot=_parse_hot(entry.get("detail_text")),
                )
            )
            if len(items) >= limit:
                break
        return items


def _parse_hot(text: str | None) -> float | None:
    """解析 "1234 万热度" / "567 万热度" 之类的文本为数值。"""
    if not text:
        return None
    try:
        num = ""
        for ch in text:
            if ch.isdigit() or ch == ".":
                num += ch
            elif num:
                break
        value = float(num) if num else 0.0
        if "万" in text:
            value *= 10000
        return value
    except ValueError:
        return None


register(ZhihuPlatform())
