"""
Layer 6: 节点注册表 (Component Registry)

Langflow 中拖拽的节点只是一个"空壳标识符"，真正的 Python 逻辑在我们的后端代码里。
这是安全防护的关键：防止 Langflow 中出现任意代码执行 (RCE) 漏洞。

架构约束：
- 所有节点函数必须接受 IncidentState 并返回 dict
- 节点只能调用 layer1 到 layer8 暴露的内部函数
- 绝对禁止在节点脚本中直接写死 SQL 查询或发起未经鉴权的外部 HTTP 请求
"""

import uuid
from typing import Callable, Dict, Any
from loguru import logger

# 导入 IncidentState 模型
from backend.src.models.incident_state import IncidentState


# ============================================
# 节点函数类型定义
# ============================================

# 节点函数签名：接受 IncidentState，返回更新后的状态字典
NodeFunction = Callable[[IncidentState], dict]


# ============================================
# Layer 2: 标准化节点
# ============================================

async def ocsf_normalizer_node(state: IncidentState) -> dict:
    """
    OCSF 标准化节点
    
    调用 Layer 2 Normalizer 将原始日志转换为 OCSF 格式
    
    Args:
        state: 当前事件状态，包含原始 event_data
        
    Returns:
        dict: 更新后的状态，包含 normalized_data
    """
    logger.info(f"[Node] OCSF_Normalizer_Node - trace_id: {state.trace_id}")
    
    # 导入 Layer 2 Normalizer
    from backend.src.data_plane.layer2_normalizer.normalizer import normalizer
    
    try:
        # 调用 Layer 2 标准化
        raw_log = state.event_data.get("raw_log", {})
        source = state.event_data.get("source", "unknown")
        
        normalized_event = await normalizer.normalize(raw_log, source)
        
        return {
            "normalized_data": normalized_event.model_dump(),
            "status": "normalized",
            "current_node": "OCSF_Normalizer_Node"
        }
    except Exception as e:
        logger.error(f"标准化失败: {e}")
        return {
            "error_message": f"标准化失败: {str(e)}",
            "status": "failed"
        }


# ============================================
# Layer 5: AI 分析节点
# ============================================

async def ai_triage_node(state: IncidentState) -> dict:
    """
    AI 威胁研判节点
    
    调用 Layer 5 Analyzer 进行智能分析
    
    Args:
        state: 当前事件状态，包含 normalized_data
        
    Returns:
        dict: 更新后的状态，包含 analysis_result
    """
    logger.info(f"[Node] AI_Triage_Node - trace_id: {state.trace_id}")
    
    # 导入 Layer 5 Analyzer
    from backend.src.data_plane.layer5_analyzer.analyzer import get_analyzer
    
    try:
        analyzer = get_analyzer()
        
        # 构建告警数据
        alert_data = {
            "id": state.alert_id or state.trace_id,
            "description": state.normalized_data.get("alert_description", ""),
            "severity": _map_severity(state.normalized_data.get("severity_id", 2)),
            "source_ip": state.normalized_data.get("src_ip"),
            "target_ip": state.normalized_data.get("dst_ip"),
            "timestamp": state.normalized_data.get("timestamp"),
        }
        
        # 调用 AI 研判
        triage_result = await analyzer.triage_alert(alert_data)
        
        return {
            "analysis_result": {
                "is_true_positive": triage_result.is_true_positive,
                "threat_level": triage_result.threat_level.value,
                "category": triage_result.category,
                "description": triage_result.description,
                "evidence": triage_result.evidence,
                "confidence": triage_result.confidence,
            },
            "status": "analyzed",
            "current_node": "AI_Triage_Node"
        }
    except Exception as e:
        logger.error(f"AI研判失败: {e}")
        return {
            "error_message": f"AI研判失败: {str(e)}",
            "status": "failed"
        }


def _map_severity(severity_id: int) -> str:
    """映射 OCSF 严重级别到字符串"""
    mapping = {
        1: "low",
        2: "medium", 
        3: "high",
        4: "critical",
        5: "critical"
    }
    return mapping.get(severity_id, "medium")


# ============================================
# Layer 8: OpenC2 执行节点
# ============================================

async def openc2_isolate_node(state: IncidentState) -> dict:
    """
    OpenC2 隔离节点
    
    调用 Layer 8 Executor 执行隔离操作
    
    重要：此节点为高危节点，会自动触发 HITL 中断
    
    Args:
        state: 当前事件状态，包含 target_ip 或 target_asset_id
        
    Returns:
        dict: 更新后的状态，包含 execution_result
    """
    logger.info(f"[Node] OpenC2_Isolate_Node - trace_id: {state.trace_id}")
    
    # 导入 Layer 8 Executor
    from backend.src.data_plane.layer8_executor.executor import get_executor, Action
    
    try:
        executor = get_executor()
        
        # 确定目标
        target = {}
        if state.target_asset_id:
            target = {"device_id": state.target_asset_id, "type": "device"}
        elif state.target_ip:
            target = {"value": state.target_ip, "type": "ipv4"}
        else:
            raise ValueError("No target specified for isolation")
        
        # 创建隔离命令
        command = executor.create_command(
            action=Action.QUARANTINE,
            target=target,
            actuator_id="edr-01",
            modifiers={"isolation_type": "network"}
        )
        
        # 执行命令
        result = await executor.execute_command(command)
        
        return {
            "execution_result": {
                "command_id": result.command_id,
                "status": result.status,
                "results": result.results,
                "timestamp": result.timestamp,
                "duration_ms": result.duration_ms
            },
            "status": "executed",
            "current_node": "OpenC2_Isolate_Node"
        }
    except Exception as e:
        logger.error(f"隔离执行失败: {e}")
        return {
            "error_message": f"隔离执行失败: {str(e)}",
            "status": "failed"
        }


async def openc2_block_ip_node(state: IncidentState) -> dict:
    """
    OpenC2 封禁 IP 节点
    
    调用 Layer 8 Executor 执行 IP 封禁操作
    
    重要：此节点为高危节点，会自动触发 HITL 中断
    
    Args:
        state: 当前事件状态，包含 attacker_ip
        
    Returns:
        dict: 更新后的状态，包含 execution_result
    """
    logger.info(f"[Node] OpenC2_Block_IP_Node - trace_id: {state.trace_id}")
    
    # 导入 Layer 8 Executor
    from backend.src.data_plane.layer8_executor.executor import get_executor, Action
    
    try:
        executor = get_executor()
        
        # 确定目标 IP
        target_ip = state.attacker_ip or state.target_ip
        if not target_ip:
            raise ValueError("No IP specified for blocking")
        
        # 创建封禁命令
        command = executor.create_command(
            action=Action.DENY,
            target={"value": target_ip, "type": "ipv4"},
            actuator_id="firewall-01",
            modifiers={"duration": 3600}  # 默认封禁1小时
        )
        
        # 执行命令
        result = await executor.execute_command(command)
        
        return {
            "execution_result": {
                "command_id": result.command_id,
                "status": result.status,
                "results": result.results,
                "timestamp": result.timestamp,
                "duration_ms": result.duration_ms
            },
            "status": "executed",
            "current_node": "OpenC2_Block_IP_Node"
        }
    except Exception as e:
        logger.error(f"IP封禁失败: {e}")
        return {
            "error_message": f"IP封禁失败: {str(e)}",
            "status": "failed"
        }


# ============================================
# HITL 审批节点
# ============================================

async def human_approval_node(state: IncidentState) -> dict:
    """
    人类审批节点
    
    此节点用于处理 HITL 审批结果。
    当前端批准或拒绝后，图会流转到此节点。
    
    Args:
        state: 当前事件状态，包含 action_approved
        
    Returns:
        dict: 更新后的状态
    """
    logger.info(f"[Node] Human_Approval_Node - trace_id: {state.trace_id}, approved: {state.action_approved}")
    
    if state.action_approved:
        return {
            "status": "approved",
            "current_node": "Human_Approval_Node"
        }
    else:
        return {
            "status": "rejected",
            "current_node": "Human_Approval_Node"
        }


# ============================================
# 通知节点
# ============================================

async def notification_node(state: IncidentState) -> dict:
    """
    通知节点
    
    发送告警通知到安全团队
    
    Args:
        state: 当前事件状态
        
    Returns:
        dict: 更新后的状态
    """
    logger.info(f"[Node] Notification_Node - trace_id: {state.trace_id}")
    
    # 导入 Layer 8 Executor (通知功能)
    from backend.src.data_plane.layer8_executor.executor import get_executor, Action
    
    try:
        executor = get_executor()
        
        # 创建通知命令
        message = f"安全事件告警: {state.trace_id}"
        command = executor.create_command(
            action=Action.NOTIFY,
            target={"type": "user", "value": "security_team"},
            actuator_id="siem-01",
            modifiers={"channels": ["email", "slack"], "message": message}
        )
        
        # 执行通知
        result = await executor.execute_command(command)
        
        return {
            "execution_result": {
                "notification": result.results,
                "status": result.status
            },
            "status": "notified",
            "current_node": "Notification_Node"
        }
    except Exception as e:
        logger.error(f"通知发送失败: {e}")
        return {
            "error_message": f"通知发送失败: {str(e)}",
            "status": "failed"
        }


# ============================================
# 结束节点
# ============================================

def end_node(state: IncidentState) -> dict:
    """
    结束节点
    
    标记流程结束
    
    Args:
        state: 当前事件状态
        
    Returns:
        dict: 最终状态
    """
    logger.info(f"[Node] End_Node - trace_id: {state.trace_id}")
    
    return {
        "status": "completed",
        "current_node": "End_Node"
    }


# ============================================
# 节点注册表
# ============================================

# 核心注册表：所有可用的节点函数
# 键为节点类型字符串，与 Langflow 导出的 JSON 中的 type 字段对应
NODE_REGISTRY: Dict[str, NodeFunction] = {
    # 标准化节点
    "OCSF_Normalizer": ocsf_normalizer_node,
    "Normalizer": ocsf_normalizer_node,
    
    # 分析节点
    "AI_Triage": ai_triage_node,
    "AI_Analysis": ai_triage_node,
    "Analyzer": ai_triage_node,
    
    # 执行节点 (高危 - 自动触发 HITL)
    "OpenC2_Isolate": openc2_isolate_node,
    "OpenC2_Block_IP": openc2_block_ip_node,
    "Isolate": openc2_isolate_node,
    "Block_IP": openc2_block_ip_node,
    
    # 审批节点
    "Human_Approval": human_approval_node,
    "Approval": human_approval_node,
    
    # 通知节点
    "Notification": notification_node,
    "Notify": notification_node,
    
    # 结束节点
    "End": end_node,
}


# ============================================
# 高危节点标识
# ============================================

# 需要 HITL 中断的高危节点类型
HIGH_RISK_NODE_TYPES = {
    "OpenC2_Isolate",
    "OpenC2_Block_IP", 
    "Isolate",
    "Block_IP",
    "Quarantine",
    "Delete",
}


def is_high_risk_node(node_type: str) -> bool:
    """
    判断节点是否为高危节点
    
    Args:
        node_type: 节点类型字符串
        
    Returns:
        bool: 是否为高危节点
    """
    return node_type in HIGH_RISK_NODE_TYPES or node_type.startswith("OpenC2_")


def get_node_function(node_type: str) -> NodeFunction:
    """
    获取节点函数
    
    Args:
        node_type: 节点类型
        
    Returns:
        NodeFunction: 节点函数
        
    Raises:
        ValueError: 节点类型未注册
    """
    if node_type not in NODE_REGISTRY:
        raise ValueError(f"Harness Error: Unauthorized node type '{node_type}' - not in registry")
    return NODE_REGISTRY[node_type]


# ============================================
# 注册新节点 (供扩展使用)
# ============================================

def register_node(node_type: str, node_function: NodeFunction, high_risk: bool = False) -> None:
    """
    注册新的节点类型
    
    Args:
        node_type: 节点类型标识
        node_function: 节点函数
        high_risk: 是否为高危节点
    """
    NODE_REGISTRY[node_type] = node_function
    
    if high_risk:
        HIGH_RISK_NODE_TYPES.add(node_type)
    
    logger.info(f"Registered node type: {node_type} (high_risk={high_risk})")
