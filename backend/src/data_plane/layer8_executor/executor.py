"""
Layer 8: 执行反馈层
OpenC2终端命令执行

功能：
- OpenC2命令封装
- 终端设备控制
- 执行结果反馈
- 动作审计
"""

import uuid
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from loguru import logger
from pydantic import BaseModel


class Action(str, Enum):
    """OpenC2动作"""
    DENY = "deny"
    ALLOW = "allow"
    CONTAIN = "contain"
    DELETE = "delete"
    RESTART = "restart"
    SCAN = "scan"
    QUARANTINE = "quarantine"
    INVESTIGATE = "investigate"
    MITIGATE = "mitigate"
    NOTIFY = "notify"


class TargetType(str, Enum):
    """目标类型"""
    IP = "ipv4"
    DOMAIN = "domain"
    FILE = "file"
    PROCESS = "process"
    USER = "user"
    DEVICE = "device"


class ActuatorType(str, Enum):
    """执行器类型"""
    FIREWALL = "firewall"
    EDR = "endpoint_detection"
    SIEM = "siem"
    NETWORK = "network_device"
    EMAIL = "email_gateway"


class OpenC2Command(BaseModel):
    """OpenC2命令"""
    id: str
    action: Action
    target: Dict[str, Any]
    actuator: Optional[Dict[str, Any]] = None
    modifiers: Optional[Dict[str, Any]] = None
    timeout: int = 30
    response_requested: bool = True


class ExecutionResult(BaseModel):
    """执行结果"""
    command_id: str
    status: str  # pending, success, failure
    results: Dict[str, Any]
    timestamp: str
    duration_ms: float


class OpenC2Executor:
    """OpenC2执行器"""
    
    def __init__(self):
        # 执行器注册表
        self.actuators: Dict[str, Dict[str, Any]] = {
            "firewall-01": {
                "type": ActuatorType.FIREWALL,
                "name": "边界防火墙",
                "capabilities": ["deny", "allow"],
                "status": "online"
            },
            "edr-01": {
                "type": ActuatorType.EDR,
                "name": "终端防护",
                "capabilities": ["quarantine", "contain", "delete"],
                "status": "online"
            },
            "siem-01": {
                "type": ActuatorType.SIEM,
                "name": "日志分析平台",
                "capabilities": ["notify", "investigate"],
                "status": "online"
            }
        }
        
        # 执行历史
        self.execution_history: List[ExecutionResult] = []
        
        # 待执行队列
        self.pending_commands: Dict[str, OpenC2Command] = {}
    
    def create_command(
        self,
        action: Action,
        target: Dict[str, Any],
        actuator_id: str = None,
        modifiers: Dict[str, Any] = None
    ) -> OpenC2Command:
        """创建OpenC2命令"""
        command = OpenC2Command(
            id=str(uuid.uuid4()),
            action=action,
            target=target,
            actuator={"actuator_id": actuator_id} if actuator_id else None,
            modifiers=modifiers or {}
        )
        
        self.pending_commands[command.id] = command
        logger.info(f"📝 创建命令: {action.value} -> {target}")
        
        return command
    
    async def execute_command(self, command: OpenC2Command) -> ExecutionResult:
        """执行命令"""
        start_time = datetime.now()
        
        # 验证执行器
        actuator_id = command.actuator.get("actuator_id") if command.actuator else None
        actuator = self.actuators.get(actuator_id) if actuator_id else None
        
        if actuator and actuator["status"] != "online":
            return ExecutionResult(
                command_id=command.id,
                status="failure",
                results={"error": f"执行器 {actuator_id} 不在线"},
                timestamp=datetime.now().isoformat(),
                duration_ms=0
            )
        
        # 模拟执行
        logger.info(f"⚡ 执行命令: {command.action.value} on {command.target}")
        
        # 根据动作类型执行
        results = await self._execute_action(command)
        
        # 计算耗时
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        execution_result = ExecutionResult(
            command_id=command.id,
            status="success",
            results=results,
            timestamp=datetime.now().isoformat(),
            duration_ms=duration
        )
        
        self.execution_history.append(execution_result)
        
        if command.id in self.pending_commands:
            del self.pending_commands[command.id]
        
        logger.info(f"✅ 命令执行完成: {command.id}, 耗时: {duration:.2f}ms")
        
        return execution_result
    
    async def _execute_action(self, command: OpenC2Command) -> Dict[str, Any]:
        """执行具体动作"""
        action = command.action
        target = command.target
        actuator_id = command.actuator.get("actuator_id") if command.actuator else None
        
        # 模拟不同动作的执行
        if action == Action.DENY:
            return await self._execute_deny(target, actuator_id)
        elif action == Action.ALLOW:
            return await self._execute_allow(target, actuator_id)
        elif action == Action.QUARANTINE:
            return await self._execute_quarantine(target, actuator_id)
        elif action == Action.CONTAIN:
            return await self._execute_contain(target, actuator_id)
        elif action == Action.DELETE:
            return await self._execute_delete(target, actuator_id)
        elif action == Action.SCAN:
            return await self._execute_scan(target, actuator_id)
        elif action == Action.NOTIFY:
            return await self._execute_notify(target, actuator_id)
        else:
            return {"message": f"动作 {action.value} 执行完成"}
    
    async def _execute_deny(self, target: Dict, actuator_id: str) -> Dict:
        """封禁IP/域名"""
        target_type = target.get("type", "ip")
        target_value = target.get("value", "unknown")
        
        # 模拟API调用
        await asyncio.sleep(0.1)
        
        return {
            "action": "deny",
            "target": target,
            "result": f"已封禁 {target_type}: {target_value}",
            "rule_id": f"rule-{uuid.uuid4().hex[:8]}"
        }
    
    async def _execute_allow(self, target: Dict, actuator_id: str) -> Dict:
        """放行"""
        await asyncio.sleep(0.05)
        
        return {
            "action": "allow",
            "target": target,
            "result": f"已放行 {target.get('value')}"
        }
    
    async def _execute_quarantine(self, target: Dict, actuator_id: str) -> Dict:
        """隔离主机"""
        device_id = target.get("device_id") or target.get("value")
        
        await asyncio.sleep(0.2)
        
        return {
            "action": "quarantine",
            "target": target,
            "result": f"已隔离设备: {device_id}",
            "isolation_type": "network"
        }
    
    async def _execute_contain(self, target: Dict, actuator_id: str) -> Dict:
        """-contain主机"""
        await asyncio.sleep(0.15)
        
        return {
            "action": "contain",
            "target": target,
            "result": f"已-contain设备: {target.get('value')}"
        }
    
    async def _execute_delete(self, target: Dict, actuator_id: str) -> Dict:
        """删除文件/进程"""
        target_type = target.get("type", "file")
        
        await asyncio.sleep(0.1)
        
        return {
            "action": "delete",
            "target_type": target_type,
            "target": target,
            "result": f"已删除{target_type}: {target.get('value')}"
        }
    
    async def _execute_scan(self, target: Dict, actuator_id: str) -> Dict:
        """扫描"""
        await asyncio.sleep(0.5)
        
        return {
            "action": "scan",
            "target": target,
            "result": "扫描完成",
            "threats_found": 0
        }
    
    async def _execute_notify(self, target: Dict, actuator_id: str) -> Dict:
        """通知"""
        await asyncio.sleep(0.05)
        
        return {
            "action": "notify",
            "target": target,
            "result": "通知已发送",
            "channels": ["email", "slack"]
        }
    
    def get_actuators(self) -> List[Dict[str, Any]]:
        """获取可用执行器"""
        return [
            {"id": k, **v}
            for k, v in self.actuators.items()
        ]
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return [
            {
                "command_id": r.command_id,
                "status": r.status,
                "timestamp": r.timestamp,
                "duration_ms": r.duration_ms
            }
            for r in self.execution_history[-limit:]
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取执行统计"""
        total = len(self.execution_history)
        success = sum(1 for r in self.execution_history if r.status == "success")
        failure = sum(1 for r in self.execution_history if r.status == "failure")
        
        avg_duration = (
            sum(r.duration_ms for r in self.execution_history) / max(1, total)
        )
        
        return {
            "total_executions": total,
            "success": success,
            "failure": failure,
            "success_rate": success / max(1, total),
            "average_duration_ms": avg_duration,
            "pending_commands": len(self.pending_commands)
        }


# 全局实例
_executor: Optional[OpenC2Executor] = None


def get_executor() -> OpenC2Executor:
    """获取全局执行器"""
    global _executor
    if _executor is None:
        _executor = OpenC2Executor()
    return _executor


# ============================================
# FastAPI 端点
# ============================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ExecuteCommandRequest(BaseModel):
    """执行命令请求"""
    action: str
    target: Dict[str, Any]
    actuator_id: Optional[str] = None
    modifiers: Optional[Dict[str, Any]] = None


@router.post("/layer8/execute")
async def execute_command(request: ExecuteCommandRequest) -> dict:
    """执行OpenC2命令"""
    executor = get_executor()
    
    try:
        action = Action(request.action)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效动作: {request.action}")
    
    command = executor.create_command(
        action=action,
        target=request.target,
        actuator_id=request.actuator_id,
        modifiers=request.modifiers
    )
    
    result = await executor.execute_command(command)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "command_id": command.id,
            "status": result.status,
            "results": result.results,
            "timestamp": result.timestamp,
            "duration_ms": result.duration_ms
        }
    }


@router.get("/layer8/actuators")
async def list_actuators() -> dict:
    """列出可用执行器"""
    executor = get_executor()
    actuators = executor.get_actuators()
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {"actuators": actuators}
    }


@router.get("/layer8/history")
async def get_history(limit: int = 50) -> dict:
    """获取执行历史"""
    executor = get_executor()
    history = executor.get_history(limit)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {"history": history, "total": len(history)}
    }


@router.get("/layer8/stats")
async def get_statistics() -> dict:
    """获取执行统计"""
    executor = get_executor()
    stats = executor.get_statistics()
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": stats
    }


@router.post("/layer8/actuators/{actuator_id}/action")
async def actuator_action(
    actuator_id: str,
    action: str,
    target: Dict[str, Any]
) -> dict:
    """执行器动作"""
    executor = get_executor()
    
    if actuator_id not in executor.actuators:
        raise HTTPException(status_code=404, detail="执行器不存在")
    
    try:
        act = Action(action)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效动作")
    
    command = executor.create_command(
        action=act,
        target=target,
        actuator_id=actuator_id
    )
    
    result = await executor.execute_command(command)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": result.status == "success",
        "data": result.results
    }
