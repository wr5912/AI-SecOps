"""
WebSocket 路由
处理前端WebSocket连接
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from .manager import websocket_manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    channel = "global"  # 默认频道
    await websocket_manager.connect(websocket, channel)
    
    try:
        while True:
            # 接收前端消息
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            
            # 可以处理前端发来的订阅请求
            # 例如: {"action": "subscribe", "channel": "hitl"}
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, channel)
        logger.info("WebSocket disconnected")


@router.websocket("/ws/{channel}")
async def websocket_channel_endpoint(websocket: WebSocket, channel: str):
    """指定频道的WebSocket连接"""
    await websocket_manager.connect(websocket, channel)
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message on channel {channel}: {data}")
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, channel)
        logger.info(f"WebSocket disconnected from channel {channel}")
