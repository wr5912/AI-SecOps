"""
Layer 3: 知识图谱层
Neo4j图数据库集成

功能：
- 资产拓扑图构建
- 攻击链路查询
- 威胁关系分析
"""

import uuid
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from datetime import datetime
from loguru import logger
from pydantic import BaseModel, Field

# 尝试导入neo4j驱动
try:
    from neo4j import GraphDatabase, Driver, Record
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j驱动不可用，使用内存模拟实现")


class AssetType(str, Enum):
    """资产类型"""
    SERVER = "server"
    ENDPOINT = "endpoint"
    DATABASE = "database"
    FIREWALL = "firewall"
    IOT = "iot"
    CLOUD = "cloud"
    USER = "user"


class NodeStatus(str, Enum):
    """节点状态"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    COMPROMISED = "compromised"
    UNKNOWN = "unknown"


class GraphNode(BaseModel):
    """图节点"""
    id: str
    name: str
    type: AssetType
    ip: Optional[str] = None
    status: NodeStatus = NodeStatus.UNKNOWN
    risk_score: int = 0
    properties: Dict[str, Any] = Field(default_factory=dict)
    labels: List[str] = Field(default_factory=list)


class GraphEdge(BaseModel):
    """图边"""
    id: str
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class AttackPath(BaseModel):
    """攻击路径"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    confidence: float
    mitre_tactics: List[str]


class Neo4jGraphClient:
    """Neo4j图数据库客户端"""
    
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password"
    ):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver: Optional[Driver] = None
        
        if NEO4J_AVAILABLE:
            try:
                self.driver = GraphDatabase.driver(uri, auth=(username, password))
                logger.info(f"Neo4j连接成功: {uri}")
            except Exception as e:
                logger.warning(f"Neo4j连接失败: {e}，使用内存模拟")
                self.driver = None
        else:
            logger.info("使用内存模拟图数据库")
        
        # 内存模拟存储
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: Dict[str, GraphEdge] = {}
        
        # 初始化示例数据
        self._init_sample_data()
    
    def _init_sample_data(self):
        """初始化示例数据"""
        # 添加示例资产节点
        sample_nodes = [
            GraphNode(
                id="fw-01",
                name="边界防火墙",
                type=AssetType.FIREWALL,
                ip="10.0.0.1",
                status=NodeStatus.NORMAL,
                risk_score=15,
                labels=["Asset", "Firewall"]
            ),
            GraphNode(
                id="srv-web-01",
                name="Web服务器-ERP",
                type=AssetType.SERVER,
                ip="10.0.0.25",
                status=NodeStatus.CRITICAL,
                risk_score=92,
                labels=["Asset", "Server", "Web"]
            ),
            GraphNode(
                id="srv-db-01",
                name="核心数据库",
                type=AssetType.DATABASE,
                ip="10.0.0.30",
                status=NodeStatus.WARNING,
                risk_score=68,
                labels=["Asset", "Database"]
            ),
            GraphNode(
                id="ep-finance-01",
                name="财务工作站",
                type=AssetType.ENDPOINT,
                ip="10.0.1.88",
                status=NodeStatus.COMPROMISED,
                risk_score=98,
                labels=["Asset", "Endpoint"]
            ),
            GraphNode(
                id="attacker-01",
                name="攻击者",
                type=AssetType.USER,
                ip="203.0.113.45",
                status=NodeStatus.CRITICAL,
                risk_score=100,
                labels=["Threat", "Attacker"]
            ),
        ]
        
        for node in sample_nodes:
            self._nodes[node.id] = node
        
        # 添加示例连接边
        sample_edges = [
            GraphEdge(
                id="e1",
                source="attacker-01",
                target="srv-web-01",
                type="ATTACKS",
                properties={"technique": "T1190", "timestamp": datetime.now().isoformat()}
            ),
            GraphEdge(
                id="e2",
                source="srv-web-01",
                target="srv-db-01",
                type="COMMUNICATES",
                properties={"protocol": "MySQL", "port": 3306}
            ),
            GraphEdge(
                id="e3",
                source="srv-web-01",
                target="ep-finance-01",
                type="LATERAL_MOVEMENT",
                properties={"technique": "T1210", "timestamp": datetime.now().isoformat()}
            ),
            GraphEdge(
                id="e4",
                source="ep-finance-01",
                target="srv-db-01",
                type="ATTEMPTS_ACCESS",
                properties={"technique": "T1110", "timestamp": datetime.now().isoformat()}
            ),
            GraphEdge(
                id="e5",
                source="fw-01",
                target="srv-web-01",
                type="PROTECTS",
                properties={}
            ),
        ]
        
        for edge in sample_edges:
            self._edges[edge.id] = edge
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
    
    # ==================== 节点操作 ====================
    
    def create_node(
        self,
        node_id: str,
        name: str,
        node_type: AssetType,
        ip: Optional[str] = None,
        labels: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> GraphNode:
        """创建节点"""
        node = GraphNode(
            id=node_id,
            name=name,
            type=node_type,
            ip=ip,
            labels=labels or ["Asset"],
            properties=properties or {}
        )
        self._nodes[node_id] = node
        
        if self.driver:
            self._create_node_neo4j(node)
        
        logger.info(f"创建节点: {node_id}")
        return node
    
    def _create_node_neo4j(self, node: GraphNode):
        """在Neo4j中创建节点"""
        try:
            with self.driver.session() as session:
                labels = ":".join(node.labels)
                query = f"""
                CREATE (n:{labels} {{id: $id, name: $name, type: $type, ip: $ip}})
                """
                session.run(query, id=node.id, name=node.name, type=node.type.value, ip=node.ip)
        except Exception as e:
            logger.debug(f"Neo4j创建节点失败: {e}")
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """获取节点"""
        return self._nodes.get(node_id)
    
    def get_all_nodes(self, labels: Optional[List[str]] = None) -> List[GraphNode]:
        """获取所有节点"""
        nodes = list(self._nodes.values())
        if labels:
            nodes = [n for n in nodes if any(l in n.labels for l in labels)]
        return nodes
    
    def update_node_status(self, node_id: str, status: NodeStatus, risk_score: int):
        """更新节点状态"""
        if node_id in self._nodes:
            self._nodes[node_id].status = status
            self._nodes[node_id].risk_score = risk_score
    
    # ==================== 边操作 ====================
    
    def create_edge(
        self,
        edge_id: str,
        source_id: str,
        target_id: str,
        edge_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Optional[GraphEdge]:
        """创建边"""
        if source_id not in self._nodes or target_id not in self._nodes:
            logger.warning(f"源或目标节点不存在: {source_id} -> {target_id}")
            return None
        
        edge = GraphEdge(
            id=edge_id,
            source=source_id,
            target=target_id,
            type=edge_type,
            properties=properties or {}
        )
        self._edges[edge_id] = edge
        
        if self.driver:
            self._create_edge_neo4j(edge)
        
        logger.info(f"创建边: {source_id} -[{edge_type}]-> {target_id}")
        return edge
    
    def _create_edge_neo4j(self, edge: GraphEdge):
        """在Neo4j中创建边"""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (a {id: $source_id})
                MATCH (b {id: $target_id})
                CREATE (a)-[r:RELATES {type: $type, id: $edge_id}]->(b)
                """
                session.run(
                    query,
                    source_id=edge.source,
                    target_id=edge.target,
                    type=edge.type,
                    edge_id=edge.id
                )
        except Exception as e:
            logger.debug(f"Neo4j创建边失败: {e}")
    
    def get_edges(self, node_id: str, direction: str = "both") -> List[GraphEdge]:
        """获取节点的边"""
        edges = []
        for edge in self._edges.values():
            if direction in ["out", "both"] and edge.source == node_id:
                edges.append(edge)
            if direction in ["in", "both"] and edge.target == node_id:
                edges.append(edge)
        return edges
    
    # ==================== 拓扑查询 ====================
    
    def get_topology(self, max_depth: int = 3) -> Dict[str, Any]:
        """获取网络拓扑"""
        nodes = []
        edges = []
        
        for node in self._nodes.values():
            nodes.append({
                "id": node.id,
                "name": node.name,
                "type": node.type.value,
                "ip": node.ip,
                "status": node.status.value,
                "risk_score": node.risk_score,
                "labels": node.labels
            })
        
        for edge in self._edges.values():
            edges.append({
                "id": edge.id,
                "source": edge.source,
                "target": edge.target,
                "type": edge.type
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
    
    def get_asset_relationships(self, asset_id: str) -> Dict[str, Any]:
        """获取资产关联关系"""
        node = self._nodes.get(asset_id)
        if not node:
            return {"node": None, "connections": []}
        
        connections = []
        
        for edge in self._edges.values():
            if edge.source == asset_id:
                target = self._nodes.get(edge.target)
                if target:
                    connections.append({
                        "direction": "outgoing",
                        "edge_type": edge.type,
                        "target": {
                            "id": target.id,
                            "name": target.name,
                            "type": target.type.value,
                            "ip": target.ip,
                            "status": target.status.value
                        }
                    })
            elif edge.target == asset_id:
                source = self._nodes.get(edge.source)
                if source:
                    connections.append({
                        "direction": "incoming",
                        "edge_type": edge.type,
                        "source": {
                            "id": source.id,
                            "name": source.name,
                            "type": source.type.value,
                            "ip": source.ip,
                            "status": source.status.value
                        }
                    })
        
        return {
            "node": {
                "id": node.id,
                "name": node.name,
                "type": node.type.value,
                "ip": node.ip,
                "status": node.status.value,
                "risk_score": node.risk_score
            },
            "connections": connections
        }
    
    def find_attack_paths(
        self,
        start_node_id: str,
        end_node_id: str,
        max_hops: int = 5
    ) -> List[AttackPath]:
        """查找攻击路径"""
        # 简化实现：BFS查找路径
        paths = []
        
        # 构建邻接表
        adjacency: Dict[str, List[str]] = {}
        for edge in self._edges.values():
            if edge.type in ["ATTACKS", "LATERAL_MOVEMENT", "ATTEMPTS_ACCESS"]:
                if edge.source not in adjacency:
                    adjacency[edge.source] = []
                adjacency[edge.source].append(edge.target)
        
        # BFS
        queue = [(start_node_id, [start_node_id])]
        visited_paths = set()
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_hops:
                continue
            
            if current == end_node_id:
                # 找到路径
                nodes = [self._nodes[nid] for nid in path if nid in self._nodes]
                path_edges = [
                    self._edges[eid]
                    for eid in self._edges
                    if self._edges[eid].source in path and self._edges[eid].target in path
                ]
                
                paths.append(AttackPath(
                    nodes=nodes,
                    edges=path_edges,
                    confidence=0.85,
                    mitre_tactics=["T1190", "T1210", "T1110"]
                ))
                continue
            
            if current in adjacency:
                for next_node in adjacency[current]:
                    if next_node not in path:
                        new_path = path + [next_node]
                        path_key = tuple(new_path)
                        if path_key not in visited_paths:
                            visited_paths.add(path_key)
                            queue.append((next_node, new_path))
        
        return paths
    
    def get_compromised_hosts(self) -> List[Dict[str, Any]]:
        """获取被攻陷的主机"""
        compromised = []
        
        for node in self._nodes.values():
            if node.status == NodeStatus.COMPROMISED:
                # 查找关联的攻击者
                attackers = []
                for edge in self._edges.values():
                    if edge.target == node.id and edge.type in ["ATTACKS", "LATERAL_MOVEMENT"]:
                        attacker = self._nodes.get(edge.source)
                        if attacker:
                            attackers.append({
                                "id": attacker.id,
                                "ip": attacker.ip,
                                "type": attacker.type.value
                            })
                
                compromised.append({
                    "node": {
                        "id": node.id,
                        "name": node.name,
                        "ip": node.ip,
                        "type": node.type.value,
                        "risk_score": node.risk_score
                    },
                    "attackers": attackers
                })
        
        return compromised
    
    # ==================== 统计查询 ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取图谱统计"""
        status_counts: Dict[str, int] = {}
        type_counts: Dict[str, int] = {}
        
        for node in self._nodes.values():
            status = node.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            node_type = node.type.value
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        
        edge_types: Dict[str, int] = {}
        for edge in self._edges.values():
            edge_types[edge.type] = edge_types.get(edge.type, 0) + 1
        
        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "by_status": status_counts,
            "by_type": type_counts,
            "edge_types": edge_types,
            "average_risk_score": sum(n.risk_score for n in self._nodes.values()) / max(1, len(self._nodes))
        }


# 全局实例
_graph_client: Optional[Neo4jGraphClient] = None


def get_graph_client() -> Neo4jGraphClient:
    """获取全局图数据库客户端"""
    global _graph_client
    if _graph_client is None:
        _graph_client = Neo4jGraphClient()
    return _graph_client


# ============================================
# FastAPI 端点
# ============================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid

router = APIRouter()


class CreateNodeRequest(BaseModel):
    """创建节点请求"""
    id: str
    name: str
    type: AssetType
    ip: Optional[str] = None
    labels: Optional[List[str]] = None
    properties: Optional[Dict[str, Any]] = None


class CreateEdgeRequest(BaseModel):
    """创建边请求"""
    source_id: str
    target_id: str
    type: str
    properties: Optional[Dict[str, Any]] = None


@router.get("/layer3/topology")
async def get_topology() -> dict:
    """获取网络拓扑"""
    client = get_graph_client()
    topology = client.get_topology()
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": topology
    }


@router.get("/layer3/nodes/{node_id}")
async def get_node(node_id: str) -> dict:
    """获取节点详情"""
    client = get_graph_client()
    node = client.get_node(node_id)
    
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "id": node.id,
            "name": node.name,
            "type": node.type.value,
            "ip": node.ip,
            "status": node.status.value,
            "risk_score": node.risk_score,
            "labels": node.labels,
            "properties": node.properties
        }
    }


@router.get("/layer3/nodes/{node_id}/relationships")
async def get_node_relationships(node_id: str) -> dict:
    """获取节点关联关系"""
    client = get_graph_client()
    relationships = client.get_asset_relationships(node_id)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": relationships
    }


@router.post("/layer3/nodes")
async def create_node(request: CreateNodeRequest) -> dict:
    """创建节点"""
    client = get_graph_client()
    node = client.create_node(
        node_id=request.id,
        name=request.name,
        node_type=request.type,
        ip=request.ip,
        labels=request.labels,
        properties=request.properties
    )
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {"id": node.id, "name": node.name}
    }


@router.post("/layer3/edges")
async def create_edge(request: CreateEdgeRequest) -> dict:
    """创建边"""
    client = get_graph_client()
    edge = client.create_edge(
        edge_id=f"e-{uuid.uuid4().hex[:8]}",
        source_id=request.source_id,
        target_id=request.target_id,
        edge_type=request.type,
        properties=request.properties
    )
    
    if not edge:
        raise HTTPException(status_code=400, detail="Failed to create edge")
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {"id": edge.id}
    }


@router.get("/layer3/attack-paths/{start_id}/{end_id}")
async def find_attack_paths(start_id: str, end_id: str, max_hops: int = 5) -> dict:
    """查找攻击路径"""
    client = get_graph_client()
    paths = client.find_attack_paths(start_id, end_id, max_hops)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "paths": [
                {
                    "nodes": [{"id": n.id, "name": n.name} for n in p.nodes],
                    "confidence": p.confidence,
                    "mitre_tactics": p.mitre_tactics
                }
                for p in paths
            ],
            "total": len(paths)
        }
    }


@router.get("/layer3/compromised")
async def get_compromised_hosts() -> dict:
    """获取被攻陷主机"""
    client = get_graph_client()
    compromised = client.get_compromised_hosts()
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "hosts": compromised,
            "total": len(compromised)
        }
    }


@router.get("/layer3/stats")
async def get_statistics() -> dict:
    """获取图谱统计"""
    client = get_graph_client()
    stats = client.get_statistics()
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": stats
    }
