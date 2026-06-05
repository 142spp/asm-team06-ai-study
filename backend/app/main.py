from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import analyze, confirm, feedback, run
from app.logging_config import setup_logging
from app.storage.db import init_db

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 스키마만 보장한다. 시연용 seed 는 자동 실행하지 않는다(POST /mock/seed 로 명시 호출).
    init_db()
    yield


app = FastAPI(title="Action Router Agent", lifespan=lifespan)

# 6-1 분석
app.include_router(analyze.router)
# 6-1~6-2 단일 그래프 (라우팅/검증/승인)
app.include_router(run.router)
# 6-3 피드백/선호
app.include_router(confirm.router)
app.include_router(feedback.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
