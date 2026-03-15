"""
编排/HITL API路由
"""

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


# ============================================
# 模拟审批数据
# ============================================

MOCK_APPROVALS = [
    {
        "id": "approval-001",
        "trace_id": "trk-approval-001",
        "type": "isolate_endpoint",
        "status": "pending",
        "target": {
            "type": "asset",
            "id": "endpoint-001",
            "name": "员工终端-01",
            "description": "隔离受攻击终端"
        },
        "action": {
            "type": "isolate",
            "parameters": {"isolation_type": "network"}
        },
        "risk_assessment": {
            "level": "high",
            "impact_scope": "单台终端，影响用户赵六的工作"
        },
        "requested_by": {
            "id": "ai-agent-001",
            "name": "AI安全分析",
            "source": "ai_copilot"
        },
        "requested_at": "2026-03-14T10:35:00Z",
        "expires_at": "2026-03-14T11:35:00Z"
    }
]


# ============================================
# API 端点
# ============================================

@router.get("/orchestration/pending")
async def get_pending_approvals() -> dict:
    """获取待审批任务列表"""
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "items": MOCK_APPROVALS,
            "total": len(MOCK_APPROVALS)
        }
    }


@router.post("/orchestration/{trace_id}/approve")
async def approve_task(trace_id: str, comment: Optional[str] = None) -> dict:
    """审批通过"""
    approval = next((a for a in MOCK_APPROVALS if a["trace_id"] == trace_id), None)
    
    if not approval:
        raise HTTPException(status_code=404, detail="Approval task not found")
    
    # 更新状态（实际应该写入数据库）
    approval["status"] = "approved"
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "message": "审批已通过",
            "trace_id": trace_id,
            "status": "approved",
            "comment": comment
        }
    }


@router.post("/orchestration/{trace_id}/reject")
async def reject_task(trace_id: str, reason: Optional[str] = None) -> dict:
    """审批拒绝"""
    approval = next((a for a in MOCK_APPROVALS if a["trace_id"] == trace_id), None)
    
    if not approval:
        raise HTTPException(status_code=404, detail="Approval task not found")
    
    # 更新状态
    approval["status"] = "rejected"
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "message": "审批已拒绝",
            "trace_id": trace_id,
            "status": "rejected",
            "reason": reason
        }
    }
