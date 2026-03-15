"""
反馈API路由
"""

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


# ============================================
# Pydantic 模型
# ============================================

class FeedbackRequest(BaseModel):
    """反馈提交请求"""
    trace_id: str
    target_type: str
    target_id: str
    feedback_type: str
    content: Optional[str] = None
    confidence_rating: Optional[int] = None


class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: str
    created_at: str
    status: str


# ============================================
# API 端点
# ============================================

@router.post("/feedback/submit")
async def submit_feedback(request: FeedbackRequest) -> dict:
    """提交运维反馈"""
    feedback_id = f"fb-{uuid.uuid4().hex[:8]}"
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "id": feedback_id,
            "created_at": "2026-03-14T10:00:00Z",
            "status": "submitted"
        }
    }


@router.get("/feedback")
async def list_feedback(trace_id: Optional[str] = None) -> dict:
    """获取反馈列表"""
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "items": []
        }
    }
