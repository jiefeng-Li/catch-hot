"""GitHub Trending 适配器。

页面抓取（无官方 API）。关键词策略：对仓库名/描述做包含过滤。
"""
import logging
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from ..config import FETCH_TIMEOUT
from .base import BasePlatform, RawItem, register

logger = logging.getLogger(__name__)

TRENDING_URL = "https://github.com/trending"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html",
}


class GithubTrendingPlatform(BasePlatform):
    name = "github"
    display_name = "GitHub Trending"

    async def fetch(self, keyword: str, limit: int = 20) -> list[RawItem]:
        async with httpx.AsyncClient(timeout=FETCH_TIMEOUT, headers=_HEADERS, follow_redirects=True) as client:
            resp = await client.get(TRENDING_URL, params={"since": "daily"})
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "lxml")
        items: list[RawItem] = []
        for row in soup.select("article.Box-row"):
            repo_a = row.select_one("h2 a")
            if repo_a is None:
                continue
            repo_name = " ".join(repo_a.get_text(strip=True).split()).replace(" / ", "/")
            href = repo_a.get("href", "")
            url = f"https://github.com{href}" if href.startswith("/") else href
            desc_p = row.select_one("p")
            summary = desc_p.get_text(strip=True) if desc_p else None
            stars_today_span = row.select_one("span.d-inline-block.float-sm-right")
            raw_hot = _parse_number(stars_today_span.get_text(strip=True)) if stars_today_span else None

            haystack = f"{repo_name} {summary or ''}"
            if keyword and keyword.lower() not in haystack.lower():
                continue
            items.append(
                RawItem(
                    title=repo_name,
                    url=url,
                    summary=summary,
                    published_at=datetime.now(timezone.utc),
                    raw_hot=raw_hot,
                )
            )
            if len(items) >= limit:
                break
        return items


def _parse_number(text: str) -> float | None:
    """解析 '1,234 stars today' 之类的文本。"""
    digits = "".join(ch for ch in text if ch.isdigit() or ch == ".")
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


register(GithubTrendingPlatform())
