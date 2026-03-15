"""
AI Copilot API路由
"""

import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
import asyncio

router = APIRouter()


# ============================================
# Pydantic 模型
# ============================================

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """聊天请求"""
    messages: list[ChatMessage]
    context: Optional[dict] = None


# ============================================
# 模拟AI响应
# ============================================

async def generate_response(prompt: str) -> AsyncGenerator[str, None]:
    """生成流式响应"""
    responses = [
        "我来分析一下当前的安全态势...",
        "根据最近的告警，发现了一个可疑的横向移动行为。",
        "攻击者IP 10.0.0.100 试图通过RDP协议连接内网主机。",
        "建议立即隔离受影响的终端设备。",
    ]
    
    for response in responses:
        await asyncio.sleep(0.5)
        yield response


# ============================================
# API 端点
# ============================================

@router.get("/copilot/chat/stream")
async def copilot_chat_stream(
    message: str,
    context: Optional[str] = None
) -> StreamingResponse:
    """AI Copilot 流式对话"""
    
    async def event_generator() -> AsyncGenerator[str, None]:
        async for chunk in generate_response(message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/copilot/chat")
async def copilot_chat(request: ChatRequest) -> dict:
    """AI Copilot 异步对话"""
    last_message = request.messages[-1].content if request.messages else ""
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "message": {
                "role": "assistant",
                "content": f"已收到您的消息: {last_message}。AI分析功能正在开发中..."
            }
        }
    }
