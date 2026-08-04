"""B站热搜适配器。

数据源：B站热搜公开接口。关键词策略同知乎：对标题做包含过滤。
"""
import logging

import httpx

from ..config import FETCH_TIMEOUT
from .base import BasePlatform, RawItem, register

logger = logging.getLogger(__name__)

HOT_SEARCH_URL = "https://api.bilibili.com/x/web-interface/search/square"
SEARCH_URL = "https://api.bilibili.com/x/web-interface/search/type"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Referer": "https://www.bilibili.com",
    "Accept": "application/json",
}


class BilibiliPlatform(BasePlatform):
    name = "bilibili"
    display_name = "B站热搜"

    async def fetch(self, keyword: str, limit: int = 20) -> list[RawItem]:
        items: list[RawItem] = []
        # 若提供 keyword，尝试使用搜索 API 获取具体结果（视频/话题/专栏等），若失败或无结果回退到热搜列表
        if keyword:
            try:
                async with httpx.AsyncClient(timeout=FETCH_TIMEOUT, headers=_HEADERS) as client:
                    # type=1 表示综合（可根据需要调整为视频/番剧等），pn/ps 控制分页
                    resp = await client.get(SEARCH_URL, params={"keyword": keyword, "search_type": "all", "page": 1, "pagesize": limit})
                    resp.raise_for_status()
                    payload = resp.json()

                if payload.get("code") == 0 and payload.get("data"):
                    # payload.data.list 可能包含多个 type 的结果，扁平化标题/链接
                    data = payload.get("data") or {}
                    lists = []
                    for k, v in data.items():
                        if isinstance(v, dict) and v.get("result"):
                            lists.extend(v.get("result") or [])
                    # 处理结果
                    for entry in lists:
                        title = (entry.get("title") or entry.get("name") or "").strip()
                        uri = entry.get("arcurl") or entry.get("url") or entry.get("link")
                        if not title:
                            continue
                        items.append(RawItem(title=title, url=uri or f"https://search.bilibili.com/all?keyword={keyword}", raw_hot=None))
                        if len(items) >= limit:
                            break
                    if items:
                        return items
            except Exception:
                logger.debug("bilibili search failed, fallback to hot-search")

        # 回退到热搜列表（原实现）
        async with httpx.AsyncClient(timeout=FETCH_TIMEOUT, headers=_HEADERS) as client:
            resp = await client.get(HOT_SEARCH_URL, params={"limit": 50})
            resp.raise_for_status()
            payload = resp.json()

        if payload.get("code") != 0:
            raise RuntimeError(f"bilibili 接口错误: code={payload.get('code')} msg={payload.get('message')}")

        for entry in (payload.get("data") or {}).get("trending", {}).get("list", []):
            title = (entry.get("show_name") or entry.get("keyword") or "").strip()
            kw = entry.get("keyword") or title
            if not title:
                continue
            if keyword and keyword.lower() not in title.lower():
                continue
            # 热搜词跳转到搜索页
            url = f"https://search.bilibili.com/all?keyword={kw}"
            items.append(RawItem(title=title, url=url, raw_hot=None))
            if len(items) >= limit:
                break
        return items


register(BilibiliPlatform())
