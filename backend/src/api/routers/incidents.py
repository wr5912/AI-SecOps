"""
告警/事件API路由
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


# ============================================
# 模拟告警数据
# ============================================

MOCK_ALERTS = [
    {
        "id": "alert-001",
        "trace_id": "trk-alert-001",
        "severity": "critical",
        "attacker_ip": "10.0.0.100",
        "victim_ip": "192.168.1.100",
        "type": "Suspicious Connection",
        "time": "2026-03-14T10:30:00Z",
        "mitre_tactic": "TA0011",
        "confidence_score": 95,
        "storyline_id": "storyline-001"
    },
    {
        "id": "alert-002",
        "trace_id": "trk-alert-002",
        "severity": "high",
        "attacker_ip": "192.168.1.100",
        "victim_ip": "192.168.1.20",
        "type": "Lateral Movement",
        "time": "2026-03-14T10:25:00Z",
        "mitre_tactic": "TA0008",
        "confidence_score": 80,
        "storyline_id": "storyline-001"
    },
    {
        "id": "alert-003",
        "trace_id": "trk-alert-003",
        "severity": "medium",
        "attacker_ip": "8.8.8.8",
        "victim_ip": "192.168.1.10",
        "type": "Firewall Allowed Traffic",
        "time": "2026-03-14T10:20:00Z",
        "mitre_tactic": None,
        "confidence_score": 45,
        "storyline_id": None
    },
]


# ============================================
# API 端点
# ============================================

@router.get("/incidents")
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
) -> dict:
    """获取告警列表"""
    filtered = MOCK_ALERTS
    
    if severity:
        filtered = [a for a in filtered if a["severity"] == severity]
    
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }
    }


@router.get("/incidents/{trace_id}")
async def get_incident(trace_id: str) -> dict:
    """获取告警详情"""
    alert = next((a for a in MOCK_ALERTS if a["trace_id"] == trace_id), None)
    
    if not alert:
        return {
            "trace_id": str(uuid.uuid4()),
            "success": False,
            "error": "Alert not found"
        }
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "incident": alert,
            "analysis": {
                "is_malicious": alert["confidence_score"] > 70,
                "mitre_tactics": [alert["mitre_tactic"]] if alert["mitre_tactic"] else [],
                "recommended_actions": ["ISOLATE_HOST", "BLOCK_IP"]
            }
        }
    }


@router.get("/storylines")
async def list_storylines() -> dict:
    """获取故事线列表"""
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "items": [
                {
                    "id": "storyline-001",
                    "trace_id": "trk-story-001",
                    "title": "APT攻击横向移动",
                    "description": "检测到攻击者在内网进行横向移动",
                    "severity": "critical",
                    "confidence_score": 85,
                    "assets": ["endpoint-001", "srv-db-001"],
                    "mitre_tactics": ["TA0008", "TA0011"],
                    "steps": [
                        {"time": "2026-03-14T10:30:00Z", "event": "检测到可疑连接", "node": "endpoint-001"},
                        {"time": "2026-03-14T10:25:00Z", "event": "横向移动尝试", "node": "srv-db-001"}
                    ],
                    "status": "active"
                }
            ]
        }
    }
