"""
告警数据模型
与前端TypeScript模型完全对齐
"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class AlertSeverity(str, Enum):
    """告警级别枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Alert(BaseModel):
    """告警模型 - 与前端完全对齐"""
    id: str
    trace_id: str
    severity: AlertSeverity
    attacker_ip: str
    victim_ip: str
    type: str
    time: str
    mitre_tactic: Optional[str] = None
    confidence_score: int
    storyline_id: Optional[str] = None
    acknowledged: bool = False


class AlertListResponse(BaseModel):
    """告警列表响应"""
    total: int
    page: int
    page_size: int
    items: list[Alert]


class IncidentDetailResponse(BaseModel):
    """告警详情响应"""
    incident: Alert
    analysis: dict
