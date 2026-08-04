"""平台适配层包。

导入此包即完成所有内置平台的注册。
新增平台：在本目录新建模块并在此处追加一行 import 即可。
"""
from .base import (  # noqa: F401
    BasePlatform,
    RawItem,
    all_platforms,
    get_platform,
    make_fingerprint,
    normalize_url,
    register,
    resolve_platforms,
)

# 内置平台注册（twitterapi.io 适配器预留：拿到 API Key 后在此追加）
from . import zhihu  # noqa: F401,E402
from . import bilibili  # noqa: F401,E402
from . import github_trending  # noqa: F401,E402
