"""
Layer 6: Langflow JSON 解析器

核心功能：将 Langflow 导出的 DAG JSON 编译为可持久化、带 HITL 的 LangGraph 状态机。

架构约束：
1. 零运行时依赖：Langflow 服务仅在设计态运行，导出 JSON，后端必须能独立编译
2. 状态纯洁性：所有图节点的数据传递必须严格符合 IncidentState Pydantic 模型
3. 强制隔离：Langflow 生成的任何节点代码，只能调用 layer1-layer8 暴露的内部函数
4. 无缝注入 trace_id：图执行的整个生命周期必须在 IncidentState 中携带 trace_id

注意：本模块不依赖 Langflow 运行时，仅解析其导出的 JSON
"""

import uuid
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field, ValidationError
from loguru import logger

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver

# 导入 IncidentState 模型
from backend.src.models.incident_state import IncidentState

# 导入节点注册表
from backend.src.data_plane.layer6_orchestrator.registry import (
    NODE_REGISTRY,
    HIGH_RISK_NODE_TYPES,
    is_high_risk_node,
    get_node_function,
)


# ============================================
# Pydantic 模型：Langflow JSON 结构
# ============================================

class LangflowNodeData(BaseModel):
    """Langflow 节点数据"""
    node_type: str = Field(alias="type")
    label: Optional[str] = None
    position: Optional[Dict[str, float]] = None
    # 节点配置参数
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True


class LangflowNode(BaseModel):
    """Langflow 节点模型"""
    id: str
    data: LangflowNodeData
    position: Optional[Dict[str, float]] = None


class LangflowEdge(BaseModel):
    """Langflow 边模型"""
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None


class LangflowFlow(BaseModel):
    """Langflow 流程模型"""
    id: str
    name: str
    description: Optional[str] = None
    nodes: List[LangflowNode]
    edges: List[LangflowEdge]
    
    class Config:
        # 允许额外字段
        extra = "allow"


# ============================================
# 解析器类
# ============================================

class LangflowParser:
    """
    Langflow JSON 解析器
    
    将 Langflow 导出的 JSON 拓扑转换为 LangGraph StateGraph
    """
    
    def __init__(
        self,
        checkpointer: Optional[BaseCheckpointSaver] = None,
        interrupt_before_high_risk: bool = True
    ):
        """
        初始化解析器
        
        Args:
            checkpointer: LangGraph 持久化检查点存储 (可选)
            interrupt_before_high_risk: 是否在高危节点前自动中断
        """
        self.checkpointer = checkpointer
        self.interrupt_before_high_risk = interrupt_before_high_risk
    
    def parse_flow(self, flow_json: Dict[str, Any]) -> LangflowFlow:
        """
        解析 Langflow JSON 为 Pydantic 模型
        
        Args:
            flow_json: Langflow 导出的 JSON 数据
            
        Returns:
            LangflowFlow: 验证后的流程模型
            
        Raises:
            ValidationError: JSON 结构验证失败
        """
        logger.info(f"Parsing Langflow flow: {flow_json.get('name', 'unnamed')}")
        
        # 兼容不同格式的 Langflow JSON
        # 格式1: { nodes: [...], edges: [...] }
        # 格式2: { flow: { nodes: [...], edges: [...] } }
        
        if "flow" in flow_json:
            flow_json = flow_json["flow"]
        
        nodes_data = flow_json.get("nodes", [])
        edges_data = flow_json.get("edges", [])
        
        # 转换为 LangflowNode 对象
        nodes = []
        for node_data in nodes_data:
            # 处理不同格式的节点数据
            if isinstance(node_data, dict):
                node_id = node_data.get("id")
                node_type = node_data.get("data", {}).get("type") or node_data.get("type", "Unknown")
                
                nodes.append(LangflowNode(
                    id=node_id,
                    data=LangflowNodeData(node_type=node_type),
                    position=node_data.get("position")
                ))
        
        # 转换为 LangflowEdge 对象
        edges = []
        for edge_data in edges_data:
            if isinstance(edge_data, dict):
                edges.append(LangflowEdge(
                    id=edge_data.get("id", str(uuid.uuid4())),
                    source=edge_data.get("source"),
                    target=edge_data.get("target"),
                    sourceHandle=edge_data.get("sourceHandle"),
                    targetHandle=edge_data.get("targetHandle")
                ))
        
        return LangflowFlow(
            id=flow_json.get("id", str(uuid.uuid4())),
            name=flow_json.get("name", "Unnamed Flow"),
            description=flow_json.get("description"),
            nodes=nodes,
            edges=edges
        )
    
    def build_graph(
        self,
        flow: LangflowFlow,
        initial_node: Optional[str] = None
    ) -> StateGraph:
        """
        从 Langflow 流程构建 LangGraph 状态机
        
        Args:
            flow: 解析后的流程模型
            initial_node: 起始节点 ID (默认第一个节点)
            
        Returns:
            StateGraph: LangGraph 状态图
            
        Raises:
            ValueError: 无效的节点类型或图结构
        """
        # 创建状态图
        workflow = StateGraph(IncidentState)
        
        # 识别高危节点列表
        high_risk_nodes: List[str] = []
        
        # 构建节点映射
        node_map: Dict[str, str] = {}  # node_id -> node_type
        
        # 1. 注册所有节点
        for node in flow.nodes:
            node_id = node.id
            node_type = node.data.node_type
            
            # 安全检查：节点类型必须在注册表中
            if node_type not in NODE_REGISTRY:
                raise ValueError(
                    f"Harness Error: Unauthorized node type '{node_type}'. "
                    f"Allowed types: {list(NODE_REGISTRY.keys())}"
                )
            
            # 获取节点函数并注册
            node_func = get_node_function(node_type)
            workflow.add_node(node_id, node_func)
            
            node_map[node_id] = node_type
            logger.info(f"Registered node: {node_id} ({node_type})")
            
            # 识别高危节点
            if self.interrupt_before_high_risk and is_high_risk_node(node_type):
                high_risk_nodes.append(node_id)
                logger.warning(f"High-risk node detected: {node_id} ({node_type}) - will trigger HITL")
        
        # 2. 构建边 (Edges)
        # 构建出边映射：node_id -> [target_ids]
        outgoing_edges: Dict[str, List[str]] = {}
        incoming_edges: Dict[str, List[str]] = {}
        
        for edge in flow.edges:
            source = edge.source
            target = edge.target
            
            if source not in outgoing_edges:
                outgoing_edges[source] = []
            outgoing_edges[source].append(target)
            
            if target not in incoming_edges:
                incoming_edges[target] = []
            incoming_edges[target].append(source)
        
        # 添加普通边
        for source, targets in outgoing_edges.items():
            if source in node_map:  # 确保源节点存在
                for target in targets:
                    if target in node_map:  # 确保目标节点存在
                        workflow.add_edge(source, target)
        
        # 3. 设置入口点
        if initial_node:
            workflow.set_entry_point(initial_node)
        elif flow.nodes:
            # 默认使用第一个节点作为入口
            workflow.set_entry_point(flow.nodes[0].id)
        
        # 4. 设置结束点
        # 找到没有出边的节点（叶子节点）作为结束候选
        leaf_nodes = []
        for node in flow.nodes:
            if node.id not in outgoing_edges or not outgoing_edges[node.id]:
                leaf_nodes.append(node.id)
        
        # 为叶子节点添加 END
        for leaf in leaf_nodes:
            if leaf in node_map:
                node_type = node_map[leaf]
                # 非结束节点才添加 END
                if node_type != "End" and leaf in outgoing_edges:
                    # 这里简化处理，实际可能需要 conditional edge
                    pass
        
        return workflow, high_risk_nodes
    
    def compile(
        self,
        flow: LangflowFlow,
        checkpointer: Optional[BaseCheckpointSaver] = None
    ) -> Any:
        """
        编译流程为可执行的 LangGraph
        
        Args:
            flow: 解析后的流程模型
            checkpointer: 持久化检查点 (可选，默认使用初始化时的)
            
        Returns:
            CompiledStateGraph: 可执行的状态图
        """
        checkpointer = checkpointer or self.checkpointer
        
        # 构建图
        workflow, high_risk_nodes = self.build_graph(flow)
        
        # 编译图
        compile_kwargs: Dict[str, Any] = {}
        
        if checkpointer:
            compile_kwargs["checkpointer"] = checkpointer
        
        # 添加高危节点中断
        if high_risk_nodes:
            compile_kwargs["interrupt_before"] = high_risk_nodes
            logger.info(f"Compiling graph with HITL interrupts before: {high_risk_nodes}")
        
        compiled = workflow.compile(**compile_kwargs)
        
        logger.info(f"Successfully compiled graph: {flow.name}")
        logger.info(f"High-risk nodes: {len(high_risk_nodes)}, Checkpointer: {checkpointer is not None}")
        
        return compiled


# ============================================
# 便捷函数
# ============================================

def build_graph_from_langflow(
    flow_json: Dict[str, Any],
    checkpointer: Optional[BaseCheckpointSaver] = None
) -> Any:
    """
    将 Langflow JSON 编译为 LangGraph 状态机
    
    这是规格书中定义的主要入口函数。
    
    Args:
        flow_json: Langflow 导出的 JSON 数据
        checkpointer: LangGraph 持久化检查点 (可选)
        
    Returns:
        CompiledStateGraph: 可执行的状态图
        
    Raises:
        ValueError: 节点类型未注册或图结构错误
    """
    parser = LangflowParser(checkpointer=checkpointer)
    
    # 解析 JSON
    flow = parser.parse_flow(flow_json)
    
    # 编译图
    return parser.compile(flow, checkpointer)


# ============================================
# 模拟剧本数据 (用于测试)
# ============================================

def get_mock_playbook_json() -> Dict[str, Any]:
    """
    获取模拟的剧本 JSON (用于测试)
    
    包含一个典型的安全响应流程：
    extract_ioc -> ai_triage -> OpenC2_Block_IP -> end
    """
    return {
        "id": "playbook-001",
        "name": "Malicious IP Blocking Flow",
        "description": "自动封禁恶意IP的响应剧本",
        "nodes": [
            {
                "id": "extract_ioc",
                "data": {"type": "OCSF_Normalizer"},
                "position": {"x": 100, "y": 100}
            },
            {
                "id": "ai_triage",
                "data": {"type": "AI_Triage"},
                "position": {"x": 300, "y": 100}
            },
            {
                "id": "block_ip",
                "data": {"type": "OpenC2_Block_IP"},
                "position": {"x": 500, "y": 100}
            },
            {
                "id": "notify",
                "data": {"type": "Notification"},
                "position": {"x": 500, "y": 250}
            },
            {
                "id": "end",
                "data": {"type": "End"},
                "position": {"x": 700, "y": 100}
            }
        ],
        "edges": [
            {"id": "e1", "source": "extract_ioc", "target": "ai_triage"},
            {"id": "e2", "source": "ai_triage", "target": "block_ip"},
            {"id": "e3", "source": "block_ip", "target": "notify"},
            {"id": "e4", "source": "block_ip", "target": "end"},
            {"id": "e5", "source": "notify", "target": "end"}
        ]
    }


def get_simple_playbook_json() -> Dict[str, Any]:
    """
    获取简化版剧本 JSON (最小测试用例)
    
    extract_ioc -> ai_triage -> OpenC2_Block_IP -> end
    """
    return {
        "id": "playbook-simple-001",
        "name": "Simple Blocking Flow",
        "nodes": [
            {"id": "extract_ioc", "data": {"type": "OCSF_Normalizer"}},
            {"id": "ai_triage", "data": {"type": "AI_Triage"}},
            {"id": "block_ip", "data": {"type": "OpenC2_Block_IP"}},
            {"id": "end", "data": {"type": "End"}}
        ],
        "edges": [
            {"id": "e1", "source": "extract_ioc", "target": "ai_triage"},
            {"id": "e2", "source": "ai_triage", "target": "block_ip"},
            {"id": "e3", "source": "block_ip", "target": "end"}
        ]
    }


# ============================================
# 图执行辅助函数
# ============================================

async def execute_playbook(
    graph: Any,
    initial_state: IncidentState,
    thread_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    执行剧本
    
    Args:
        graph: 编译后的 LangGraph
        initial_state: 初始状态
        thread_config: 线程配置
        
    Returns:
        Dict: 执行结果
    """
    result = await graph.ainvoke(initial_state, config=thread_config)
    return result


async def resume_after_approval(
    graph: Any,
    thread_config: Dict[str, Any],
    approved: bool = True,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    在 HITL 审批后恢复执行
    
    Args:
        graph: 编译后的 LangGraph
        thread_config: 线程配置
        approved: 是否批准
        comment: 审批意见
        
    Returns:
        Dict: 执行结果
    """
    # 获取当前状态
    current_state = await graph.aget_state(config=thread_config)
    
    # 更新状态
    updates = {
        "action_approved": approved,
        "status": "approved" if approved else "rejected"
    }
    
    if comment:
        updates["approval_comment"] = comment
    
    # 更新状态并恢复执行
    await graph.aupdate_state(
        config=thread_config,
        values=updates
    )
    
    # 继续执行
    result = await graph.ainvoke(None, config=thread_config)
    return result
