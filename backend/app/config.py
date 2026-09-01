"""全局配置项。

所有可调参数集中在此处，可通过环境变量覆盖。
"""
import os
from pathlib import Path
from urllib.parse import quote_plus

# 项目根目录（CatchHot/）
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 数据目录（日志等本地文件）
DATA_DIR = Path(os.getenv("CATCHHOT_DATA_DIR", BASE_DIR / "data"))

# MySQL 连接参数（可通过 CATCHHOT_DATABASE_URL 整体覆盖）
MYSQL_HOST = os.getenv("CATCHHOT_MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("CATCHHOT_MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("CATCHHOT_MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("CATCHHOT_MYSQL_PASSWORD", "3121")
MYSQL_DATABASE = os.getenv("CATCHHOT_MYSQL_DATABASE", "catchhot")

_DEFAULT_MYSQL_URL = (
    f"mysql+pymysql://{quote_plus(MYSQL_USER)}:{quote_plus(MYSQL_PASSWORD)}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
)

# 数据库连接串；测试环境可通过环境变量切换为 sqlite:///:memory:
DATABASE_URL = os.getenv("CATCHHOT_DATABASE_URL", _DEFAULT_MYSQL_URL)

# 抓取超时（秒）
FETCH_TIMEOUT = float(os.getenv("CATCHHOT_FETCH_TIMEOUT", "15"))

# 抓取失败最大重试次数（不含首次）
FETCH_MAX_RETRIES = int(os.getenv("CATCHHOT_FETCH_MAX_RETRIES", "2"))

# 热点列表默认返回条数（需求 7.4 验收标准）
HOT_ITEMS_DEFAULT_LIMIT = 50

# 热度归一化目标区间 [0, HOT_SCORE_MAX]
HOT_SCORE_MAX = 100.0

# 无热度数据默认分值（需求 7.3 验收标准）
DEFAULT_HOT_SCORE = 0.0

# 标题相似度去重阈值（difflib ratio，0~1）
TITLE_SIMILARITY_THRESHOLD = 0.9

# 数据保留天数（需求 9.2）
HOT_ITEM_RETENTION_DAYS = 90
JOB_RETENTION_DAYS = 30

# 前端跨域（开发期 Vue dev server 端口）
# CORS allowed origins: comma-separated list via CATCHHOT_CORS_ORIGINS.
# Default "*" allows any origin; with credentials Starlette reflects the request origin.
_CORS_ORIGINS_ENV = os.getenv("CATCHHOT_CORS_ORIGINS")
CORS_ORIGINS = (
    [item.strip() for item in _CORS_ORIGINS_ENV.split(",") if item.strip()]
    if _CORS_ORIGINS_ENV
    else ["*"]
)
