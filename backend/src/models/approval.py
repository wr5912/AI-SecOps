"""
审批/HITL数据模型
与前端TypeScript模型完全对齐
"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ApprovalStatus(str, Enum):
    """审批状态枚举"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRequestType(str, Enum):
    """审批请求类型"""
    ISOLATION = "isolation"
    BLOCK_IP = "block_ip"
    QUARANTINE = "quarantine"
    SCRIPT_EXECUTION = "script_execution"


class ApprovalRequestTarget(BaseModel):
    """审批目标"""
    type: str
    id: str
    name: str
    description: Optional[str] = None


class ApprovalRequestAction(BaseModel):
    """审批动作"""
    type: ApprovalRequestType
    parameters: dict = {}


class ApprovalRequestRiskAssessment(BaseModel):
    """风险评估"""
    level: str
    impact_scope: str


class ApprovalRequestRequester(BaseModel):
    """请求者"""
    id: str
    name: str
    source: str


class ApprovalRequest(BaseModel):
    """审批请求模型 - 与前端完全对齐"""
    id: str
    type: ApprovalRequestType
    target: str
    description: str
    requester: str
    requestTime: str
    status: ApprovalStatus
    approver: Optional[str] = None
    approveTime: Optional[str] = None
    traceId: Optional[str] = None
    priority: str


class ApprovalRequestDetail(BaseModel):
    """审批请求详情"""
    id: str
    trace_id: str
    type: ApprovalRequestType
    status: ApprovalStatus
    target: ApprovalRequestTarget
    action: ApprovalRequestAction
    risk_assessment: ApprovalRequestRiskAssessment
    requested_by: ApprovalRequestRequester
    requested_at: str
    expires_at: Optional[str] = None


class ApprovalListResponse(BaseModel):
    """审批列表响应"""
    items: list[ApprovalRequestDetail]
    total: int
