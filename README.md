# CatchHot 热点监控平台

CatchHot 是一个多平台热点采集与监控系统：定时抓取知乎热榜、B 站热搜、GitHub Trending 等平台内容，按关键词过滤、去重并归一化热度，提供热点列表、趋势分析、任务日志与标签管理等能力，前后端均支持 Docker 部署。

## 功能特性

- **标签管理**：标签增删改、启停、独立抓取频率，逻辑删除保留历史数据。
- **多平台抓取**：已接入知乎热榜、B 站热搜、GitHub Trending；平台适配层设计，新增平台无需改动核心代码。
- **数据清洗与去重**：URL 规范化指纹 + 标题相似度双重去重，热度 min-max 归一化到 [0, 100]。
- **热点列表**：按标签 / 平台 / 关键词 / 时间范围筛选，支持时间、热度排序与分页。
- **趋势分析**：按天聚合抓取数量与热度总量，平台分布可视化（ECharts）。
- **任务调度**：APScheduler 定时抓取，任务日志可追踪状态、重试次数、抓取/入库数量与错误信息。
- **复合评分**：多维度综合评分（`score`）与附加元信息（`meta`），便于列表排序与展示。
- **数据重置**：一键清空热点与任务历史并重新抓取，便于验证。

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 后端 | Python 3.10 + FastAPI + SQLAlchemy 2 + MySQL 5.7 |
| 调度 | APScheduler 3.x（AsyncIOScheduler） |
| 抓取 | httpx（异步）+ BeautifulSoup4 / lxml |
| 前端 | Vue 3.5 + Vite 5 + Element Plus + ECharts |
| 测试 | pytest + FastAPI TestClient（内存 SQLite） |
| 部署 | Docker（后端、前端独立镜像） |

## 项目结构

```
CatchHot/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── main.py           # 应用入口（lifespan 启动调度器）
│   │   ├── config.py         # 全局配置（可用环境变量覆盖）
│   │   ├── database.py       # 数据库引擎 / 会话 / 初始化
│   │   ├── models.py         # Tag / Job / HotItem
│   │   ├── schemas.py        # Pydantic 请求响应模型
│   │   ├── platforms/        # 平台适配层（zhihu / bilibili / github_trending）
│   │   ├── services/         # 抓取执行与调度器服务
│   │   └── routers/          # tags / items / fetch API 路由
│   └── tests/                # 自动化测试
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── api.js            # axios 封装（标签 / 热点 / 趋势 / 任务）
│   │   ├── router.js         # /hot /tags /trend /jobs
│   │   └── views/            # HotItems / Tags / Trend / Jobs
│   ├── Dockerfile            # 前端镜像（nginx 托管静态资源并代理 /api）
│   └── nginx.conf            # 静态资源 + /api 反向代理
├── scripts/                  # 数据迁移与评分回填脚本
├── docs/                     # 需求文档与开发文档
├── mysql_schema.sql          # 建表 SQL
├── mysql_inserts.sql         # 历史数据导入 SQL（可选）
├── Dockerfile                # 后端镜像
└── requirements.txt          # Python 依赖
```

## 快速开始

### 后端

```bash
pip install -r requirements.txt

# 可选：通过环境变量配置 MySQL（默认指向内网共享库）
# export CATCHHOT_MYSQL_HOST=127.0.0.1
# export CATCHHOT_MYSQL_PASSWORD=your-password

python -m uvicorn backend.app.main:app --reload --port 8000
```

- 启动后 API 文档：http://127.0.0.1:8000/docs
- 数据库建表：执行根目录 `mysql_schema.sql`；如需导入历史数据，可执行 `mysql_inserts.sql`。

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173，开发服务器会把 `/api` 代理到 http://127.0.0.1:8000。

### 后端配置（环境变量）

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `CATCHHOT_DATABASE_URL` | 由分项参数拼接 | 完整连接串，设置后优先于分项配置 |
| `CATCHHOT_MYSQL_HOST` | `10.25.101.149` | MySQL 主机 |
| `CATCHHOT_MYSQL_PORT` | `3306` | MySQL 端口 |
| `CATCHHOT_MYSQL_USER` | `root` | 用户名 |
| `CATCHHOT_MYSQL_PASSWORD` | 见部署配置 | 密码 |
| `CATCHHOT_MYSQL_DATABASE` | `catchhot` | 数据库名 |

> 前端构建地址通过构建参数 `VITE_API_BASE_URL` 注入（默认 `/api`，生产环境由 nginx 代理到后端）。

## Docker 部署

```bash
# 后端
docker build -t catchhot-backend .
docker run -d -p 8000:8000 catchhot-backend

# 前端（nginx 静态托管，/api 反向代理到后端）
docker build -t catchhot-frontend ./frontend
docker run -d -p 8080:80 catchhot-frontend
```

前端镜像中的 `/api` 反向代理目标在 `frontend/nginx.conf` 中配置，云平台部署时按环境调整为后端服务地址（如容器名或内网域名 + 端口）。

## 测试

```bash
python -m pytest
```

测试使用内存 SQLite 隔离，覆盖去重、热度归一化、标签与热点 API 等场景。

## 相关文档

- [需求文档](./docs/需求.md)
- [开发文档](./docs/开发文档.md)（技术选型、已实现功能、启动方式、如何新增平台）

## 说明

- 系统暂不区分用户、无登录鉴权：所有访问者共享同一份标签、热点与任务数据。
- 调度器使用内存 JobStore，服务重启后会从数据库重建任务，但错过的时间窗口不会补跑。
