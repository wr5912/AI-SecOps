"""
Layer 6: 智能编排层
负责安全响应自动化(SOAR)、剧本编排、人机协作
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from pydantic import BaseModel, Field
from loguru import logger


class ActionType(str, Enum):
    """操作类型"""
    BLOCK_IP = "block_ip"
    ISOLATE_ENDPOINT = "isolate_endpoint"
    QUARANTINE_FILE = "quarantine_file"
    DISABLE_USER = "disable_user"
    SEND_NOTIFICATION = "send_notification"
    CREATE_TICKET = "create_ticket"
    ENRICH_THREAT = "enrich_threat"
    ESCALATE = "escalate"


class ActionStatus(str, Enum):
    """操作状态"""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class PlaybookAction(BaseModel):
    """剧本动作"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: ActionType
    target: dict
    parameters: dict = {}
    order: int = 0


class Playbook(BaseModel):
    """响应剧本"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    trigger_conditions: dict
    actions: List[PlaybookAction]
    auto_execute: bool = False
    approval_required: bool = True
    status: str = "active"


class OrchestratedAction(BaseModel):
    """编排操作"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = Field(default_factory=lambda: f"trk-action-{uuid.uuid4().hex[:8]}")
    action_type: ActionType
    target: dict
    parameters: dict = {}
    status: ActionStatus = ActionStatus.PENDING
    playbook_id: Optional[str] = None
    requested_by: str = "ai_system"
    approved_by: Optional[str] = None
    executed_at: Optional[datetime] = None
    result: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SecurityOrchestrator:
    """
    安全编排器
    1. 剧本管理
    2. 自动化响应
    3. 人机协作(HITL)
    4. 操作审计
    """
    
    def __init__(self):
        self.playbooks: Dict[str, Playbook] = {}
        self.actions: Dict[str, OrchestratedAction] = {}
        self.stats = {
            "total_actions": 0,
            "pending_approvals": 0,
            "executed": 0,
            "failed": 0
        }
        
        # 初始化默认剧本
        self._init_default_playbooks()
    
    def _init_default_playbooks(self):
        """初始化默认剧本"""
        # 高危告警自动隔离剧本
        playbook1 = Playbook(
            name="High Severity Alert Response",
            description="自动隔离高危告警涉及的主机",
            trigger_conditions={"severity": "critical"},
            actions=[
                PlaybookAction(
                    action_type=ActionType.ISOLATE_ENDPOINT,
                    target={"type": "asset"},
                    parameters={"isolation_type": "network"},
                    order=1
                ),
                PlaybookAction(
                    action_type=ActionType.SEND_NOTIFICATION,
                    target={"type": "security_team"},
                    parameters={"channel": "slack"},
                    order=2
                )
            ],
            auto_execute=False,
            approval_required=True
        )
        
        # 恶意IP封禁剧本
        playbook2 = Playbook(
            name="Malicious IP Blocking",
            description="自动封禁恶意IP",
            trigger_conditions={"threat_type": "malicious_ip"},
            actions=[
                PlaybookAction(
                    action_type=ActionType.BLOCK_IP,
                    target={"type": "firewall"},
                    parameters={"duration": 3600},
                    order=1
                )
            ],
            auto_execute=False,
            approval_required=True
        )
        
        self.playbooks[playbook1.id] = playbook1
        self.playbooks[playbook2.id] = playbook2
    
    async def create_action(
        self,
        action_type: ActionType,
        target: dict,
        parameters: dict = None,
        playbook_id: str = None,
        requested_by: str = "ai_system"
    ) -> OrchestratedAction:
        """创建操作"""
        action = OrchestratedAction(
            action_type=action_type,
            target=target,
            parameters=parameters or {},
            playbook_id=playbook_id,
            requested_by=requested_by
        )
        
        self.actions[action.id] = action
        self.stats["total_actions"] += 1
        self.stats["pending_approvals"] += 1
        
        logger.info(f"Created action: {action.id} ({action_type.value})")
        return action
    
    async def approve_action(
        self,
        action_id: str,
        approved_by: str
    ) -> OrchestratedAction:
        """批准操作"""
        if action_id not in self.actions:
            raise ValueError("Action not found")
        
        action = self.actions[action_id]
        action.status = ActionStatus.APPROVED
        action.approved_by = approved_by
        
        self.stats["pending_approvals"] -= 1
        self.stats["executed"] += 1
        
        # 模拟执行
        action = await self._execute_action(action)
        
        return action
    
    async def reject_action(
        self,
        action_id: str,
        reason: str
    ) -> OrchestratedAction:
        """拒绝操作"""
        if action_id not in self.actions:
            raise ValueError("Action not found")
        
        action = self.actions[action_id]
        action.status = ActionStatus.REJECTED
        action.result = {"reason": reason}
        
        self.stats["pending_approvals"] -= 1
        
        return action
    
    async def _execute_action(self, action: OrchestratedAction) -> OrchestratedAction:
        """执行操作"""
        action.status = ActionStatus.EXECUTING
        action.executed_at = datetime.utcnow()
        
        # 模拟执行结果
        if action.action_type == ActionType.BLOCK_IP:
            action.result = {
                "status": "success",
                "message": f"IP {action.target.get('ip')} blocked successfully"
            }
        elif action.action_type == ActionType.ISOLATE_ENDPOINT:
            action.result = {
                "status": "success",
                "message": f"Endpoint {action.target.get('asset_id')} isolated"
            }
        elif action.action_type == ActionType.SEND_NOTIFICATION:
            action.result = {
                "status": "success",
                "message": "Notification sent"
            }
        else:
            action.result = {
                "status": "success",
                "message": f"Action {action.action_type.value} executed"
            }
        
        action.status = ActionStatus.COMPLETED
        logger.info(f"Action executed: {action.id}")
        
        return action
    
    async def get_action(self, action_id: str) -> Optional[OrchestratedAction]:
        """获取操作"""
        return self.actions.get(action_id)
    
    async def get_pending_actions(self) -> List[OrchestratedAction]:
        """获取待审批操作"""
        return [
            a for a in self.actions.values()
            if a.status == ActionStatus.PENDING
        ]
    
    def get_playbook(self, playbook_id: str) -> Optional[Playbook]:
        """获取剧本"""
        return self.playbooks.get(playbook_id)
    
    def get_stats(self) -> dict:
        """获取统计"""
        return {
            **self.stats,
            "active_playbooks": len([p for p in self.playbooks.values() if p.status == "active"])
        }


# 全局实例
orchestrator = SecurityOrchestrator()


# ============================================
# API 端点
# ============================================

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/layer6/actions")
async def create_action(
    action_type: ActionType,
    target: dict,
    parameters: dict = None,
    playbook_id: str = None,
    requested_by: str = "ai_system"
) -> dict:
    """创建操作"""
    action = await orchestrator.create_action(
        action_type, target, parameters, playbook_id, requested_by
    )
    return {
        "trace_id": action.trace_id,
        "success": True,
        "data": action.model_dump()
    }


@router.post("/layer6/actions/{action_id}/approve")
async def approve_action(action_id: str, approved_by: str) -> dict:
    """批准操作"""
    action = await orchestrator.approve_action(action_id, approved_by)
    return {
        "trace_id": action.trace_id,
        "success": True,
        "data": action.model_dump()
    }


@router.post("/layer6/actions/{action_id}/reject")
async def reject_action(action_id: str, reason: str) -> dict:
    """拒绝操作"""
    action = await orchestrator.reject_action(action_id, reason)
    return {
        "trace_id": action.trace_id,
        "success": True,
        "data": action.model_dump()
    }


@router.get("/layer6/actions/pending")
async def get_pending_actions() -> dict:
    """获取待审批操作"""
    actions = await orchestrator.get_pending_actions()
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "items": [a.model_dump() for a in actions],
            "total": len(actions)
        }
    }


@router.get("/layer6/playbooks")
async def list_playbooks() -> dict:
    """列出剧本"""
    playbooks = list(orchestrator.playbooks.values())
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "items": [p.model_dump() for p in playbooks],
            "total": len(playbooks)
        }
    }


@router.get("/layer6/stats")
async def get_orchestrator_stats() -> dict:
    """获取编排器统计"""
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": orchestrator.get_stats()
    }
