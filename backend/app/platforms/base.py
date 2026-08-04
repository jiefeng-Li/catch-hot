"""平台适配层基类与注册表。

新增平台只需：
1. 在本目录新建文件，继承 BasePlatform，实现 fetch()
2. 在文件末尾调用 register(YourPlatform())
无需修改任何核心流程代码（需求 8.3 适配器模式）。
"""
import hashlib
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# 去除这些跟踪参数以保证指纹稳定
_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "spm", "ref", "from", "source", "share_source", "vd_source",
}


def normalize_url(url: str) -> str:
    """URL 规范化：小写协议/域名、去末尾斜杠、去跟踪参数。"""
    url = url.strip()
    parts = urlsplit(url)
    scheme = parts.scheme.lower() or "https"
    netloc = parts.netloc.lower()
    query = urlencode(
        sorted((k, v) for k, v in parse_qsl(parts.query) if k.lower() not in _TRACKING_PARAMS)
    )
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((scheme, netloc, path, query, ""))


def make_fingerprint(url: str) -> str:
    """基于规范化链接生成去重指纹（SHA1）。"""
    return hashlib.sha1(normalize_url(url).encode("utf-8")).hexdigest()


@dataclass
class RawItem:
    """平台返回的原始数据（尚未归一化热度）。"""

    title: str
    url: str
    summary: str | None = None
    published_at: "object | None" = None  # datetime 或 None
    raw_hot: float | None = None  # 平台原生热度（可空）
    extra: dict = field(default_factory=dict)


class BasePlatform:
    """平台适配器基类。"""

    #: 平台唯一标识（小写英文），如 "zhihu"
    name: str = ""
    #: 展示名
    display_name: str = ""

    async def fetch(self, keyword: str, limit: int = 20) -> list[RawItem]:
        """按关键词抓取内容，返回标准化原始条目列表。

        实现方应自行处理平台侧错误并抛出异常，由调度层负责重试与记录。
        """
        raise NotImplementedError

    def normalize_hot(self, raw_hot: float | None, all_raw: list[float]) -> float:
        """热度归一化：将本批次原始热度映射到 [0, HOT_SCORE_MAX]。

        默认策略：min-max 归一化；无热度数据返回默认值。
        子类可重写以实现平台特定策略。
        """
        from ..config import DEFAULT_HOT_SCORE, HOT_SCORE_MAX

        if raw_hot is None:
            return DEFAULT_HOT_SCORE
        valid = [v for v in all_raw if v is not None]
        if not valid:
            return DEFAULT_HOT_SCORE
        lo, hi = min(valid), max(valid)
        if hi <= lo:
            return HOT_SCORE_MAX if raw_hot >= hi else DEFAULT_HOT_SCORE
        return round((raw_hot - lo) / (hi - lo) * HOT_SCORE_MAX, 2)


# ---------- 注册表 ----------

_REGISTRY: dict[str, BasePlatform] = {}


def register(platform: BasePlatform) -> None:
    if not platform.name:
        raise ValueError("platform.name 不能为空")
    _REGISTRY[platform.name] = platform


def get_platform(name: str) -> BasePlatform | None:
    return _REGISTRY.get(name)


def all_platforms() -> dict[str, BasePlatform]:
    return dict(_REGISTRY)


def resolve_platforms(names: list[str] | None) -> list[BasePlatform]:
    """按标签配置解析平台列表；None/空 表示全部已注册平台。"""
    if not names:
        return list(_REGISTRY.values())
    return [_REGISTRY[n] for n in names if n in _REGISTRY]
