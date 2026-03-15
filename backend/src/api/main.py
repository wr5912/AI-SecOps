"""
FastAPI 应用入口
AI-SecOps 企业智能安全运营平台
"""

import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

# 导入路由
from src.api.routers import (
    assets,
    topology,
    incidents,
    orchestration,
    feedback,
    copilot,
)

# 导入WebSocket
from src.api.websockets import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 AI-SecOps Backend Starting...")
    
    yield
    logger.info("🧹 AI-SecOps Backend Shutting down...")


# 创建FastAPI应用
app = FastAPI(
    title="AI-SecOps API",
    description="AI-SecOps 企业智能安全运营平台 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(assets.router, prefix="/api/v1", tags=["资产"])
app.include_router(topology.router, prefix="/api/v1", tags=["拓扑"])
app.include_router(incidents.router, prefix="/api/v1", tags=["告警"])
app.include_router(orchestration.router, prefix="/api/v1", tags=["编排"])
app.include_router(feedback.router, prefix="/api/v1", tags=["反馈"])
app.include_router(copilot.router, prefix="/api/v1", tags=["Copilot"])

# 注册WebSocket路由
app.include_router(ws_router, tags=["WebSocket"])


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "trace_id": str(uuid.uuid4()),
            "success": False,
            "error": str(exc),
            "detail": "Internal server error"
        }
    )


# 健康检查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


# 根路径
@app.get("/")
async def root():
    return {
        "message": "AI-SecOps API",
        "version": "1.0.0",
        "docs": "/docs"
    }
