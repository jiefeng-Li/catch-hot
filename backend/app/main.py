"""FastAPI 应用入口。

启动方式（项目根目录）：
    uvicorn backend.app.main:app --reload --port 8000
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .database import init_db
from .routers import fetch, items, tags
from .services.scheduler import scheduler_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler_service.start()
    yield
    scheduler_service.shutdown()


app = FastAPI(title="CatchHot", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tags.router)
app.include_router(items.router)
app.include_router(fetch.router)


@app.get("/api/health")
def health():
    from .platforms import all_platforms

    return {"status": "ok", "platforms": list(all_platforms())}
