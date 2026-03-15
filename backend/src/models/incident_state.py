"""
IncidentState Pydantic 模型
用于 LangGraph 状态机流转的严格类型定义

遵循架构约束：
1. 所有图节点的数据传递必须严格符合 IncidentState Pydantic 模型
2. 禁止使用无类型的 dict 或 **kwargs
3. 全程携带 trace_id 用于 WebSocket HITL 事件触发
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class IncidentState(BaseModel):
    """
    事件状态模型 - LangGraph StateGraph 的唯一状态类型
    
    所有节点之间的数据流转必须通过此模型传递，
    确保类型安全和可追溯性。
    """
    
    # ==================== 核心追踪字段 ====================
    trace_id: str = Field(
        default_factory=lambda: f"trk-{uuid.uuid4().hex[:12]}",
        description="分布式追踪ID，用于全链路追踪和WebSocket HITL事件触发"
    )
    
    # ==================== 网络实体标识 ====================
    target_ip: Optional[str] = Field(default=None, description="目标IP地址")
    attacker_ip: Optional[str] = Field(default=None, description="攻击者IP地址")
    target_asset_id: Optional[str] = Field(default=None, description="目标资产ID")
    
    # ==================== 事件数据 ====================
    alert_id: Optional[str] = Field(default=None, description="关联告警ID")
    event_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="原始事件数据"
    )
    
    # ==================== 处理结果流转 ====================
    normalized_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="OCSF标准化后的事件数据"
    )
    
    analysis_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="AI分析/研判结果"
    )
    
    # ==================== 编排控制字段 ====================
    action_approved: bool = Field(
        default=False,
        description="HITL审批状态，false表示需要人工审批"
    )
    
    approval_id: Optional[str] = Field(
        default=None,
        description="审批请求ID"
    )
    
    approval_comment: Optional[str] = Field(
        default=None,
        description="审批意见"
    )
    
    # ==================== 执行结果 ====================
    execution_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="OpenC2命令执行结果"
    )
    
    # ==================== 状态追踪 ====================
    current_node: Optional[str] = Field(
        default=None,
        description="当前执行的节点ID"
    )
    
    execution_path: List[str] = Field(
        default_factory=list,
        description="执行路径记录，用于调试和审计"
    )
    
    status: str = Field(
        default="pending",
        description="当前状态: pending, processing, awaiting_approval, approved, rejected, completed, failed"
    )
    
    error_message: Optional[str] = Field(
        default=None,
        description="错误信息"
    )
    
    # ==================== 时间戳 ====================
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="最后更新时间"
    )
    
    # ==================== 元数据 ====================
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="扩展元数据"
    )
    
    def add_execution_step(self, node_id: str) -> None:
        """记录执行步骤"""
        self.execution_path.append(node_id)
        self.current_node = node_id
        self.updated_at = datetime.utcnow()
    
    def approve(self, approval_id: str, comment: Optional[str] = None) -> None:
        """审批通过"""
        self.action_approved = True
        self.approval_id = approval_id
        self.approval_comment = comment
        self.status = "approved"
        self.updated_at = datetime.utcnow()
    
    def reject(self, approval_id: str, reason: str) -> None:
        """审批拒绝"""
        self.action_approved = False
        self.approval_id = approval_id
        self.approval_comment = reason
        self.status = "rejected"
        self.updated_at = datetime.utcnow()
    
    def mark_completed(self, result: Optional[Dict[str, Any]] = None) -> None:
        """标记完成"""
        self.status = "completed"
        if result:
            self.execution_result = result
        self.updated_at = datetime.utcnow()
    
    def mark_failed(self, error: str) -> None:
        """标记失败"""
        self.status = "failed"
        self.error_message = error
        self.updated_at = datetime.utcnow()
    
    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = False  # 保持枚举类型而非字符串值


# ============================================
# 辅助函数
# ============================================

def create_initial_state(
    trace_id: Optional[str] = None,
    alert_id: Optional[str] = None,
    target_ip: Optional[str] = None,
    attacker_ip: Optional[str] = None,
    **kwargs
) -> IncidentState:
    """
    创建初始事件状态
    
    Args:
        trace_id: 自定义trace_id，默认自动生成
        alert_id: 关联的告警ID
        target_ip: 目标IP
        attacker_ip: 攻击者IP
        **kwargs: 其他可选字段
    
    Returns:
        IncidentState: 初始状态实例
    """
    return IncidentState(
        trace_id=trace_id or f"trk-{uuid.uuid4().hex[:12]}",
        alert_id=alert_id,
        target_ip=target_ip,
        attacker_ip=attacker_ip,
        event_data=kwargs.get("event_data", {}),
        status="pending"
    )


def create_test_state(**overrides) -> IncidentState:
    """
    创建测试用状态
    
    用于单元测试和集成测试
    """
    defaults = {
        "trace_id": "test-trace-001",
        "alert_id": "alert-001",
        "target_ip": "192.168.1.100",
        "attacker_ip": "10.0.0.5",
        "target_asset_id": "asset-001",
        "event_data": {
            "source": "suricata",
            "signature": "ET SCAN Potential SSH Scan",
            "severity": 2
        },
        "status": "pending"
    }
    defaults.update(overrides)
    return IncidentState(**defaults)
