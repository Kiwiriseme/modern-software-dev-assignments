from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .db import init_db
from .routers import action_items, notes

_settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(
    title=_settings.APP_TITLE,
    version=_settings.APP_VERSION,
    lifespan=lifespan,
)

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/", response_class=HTMLResponse)# 首页 捕获请求并返回 HTML 文件内容
def index() -> str:
    html_path = _settings.FRONTEND_DIR / "index.html" 
    return html_path.read_text(encoding="utf-8")


app.include_router(notes.router)
app.include_router(action_items.router)

app.mount("/static", StaticFiles(directory=str(_settings.FRONTEND_DIR)), name="static")