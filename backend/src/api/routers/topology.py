"""
拓扑图API路由
"""

import uuid
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()


# ============================================
# 模拟拓扑数据
# ============================================

MOCK_NODES = [
    {
        "id": "srv-web-001",
        "type": "server",
        "label": "Web服务器-01",
        "ip": "192.168.1.10",
        "status": "normal",
        "risk_score": 25,
        "x": 400,
        "y": 200
    },
    {
        "id": "srv-db-001",
        "type": "database",
        "label": "数据库服务器-01",
        "ip": "192.168.1.20",
        "status": "warning",
        "risk_score": 65,
        "x": 600,
        "y": 300
    },
    {
        "id": "fw-edge-001",
        "type": "firewall",
        "label": "边界防火墙",
        "ip": "192.168.1.1",
        "status": "normal",
        "risk_score": 10,
        "x": 200,
        "y": 200
    },
    {
        "id": "endpoint-001",
        "type": "endpoint",
        "label": "员工终端-01",
        "ip": "192.168.1.100",
        "status": "critical",
        "risk_score": 85,
        "x": 100,
        "y": 300
    },
    {
        "id": "endpoint-002",
        "type": "endpoint",
        "label": "员工终端-02",
        "ip": "192.168.1.101",
        "status": "normal",
        "risk_score": 15,
        "x": 100,
        "y": 400
    },
    {
        "id": "cloud-001",
        "type": "cloud",
        "label": "云服务器",
        "ip": "10.0.0.5",
        "status": "normal",
        "risk_score": 20,
        "x": 800,
        "y": 200
    },
]

MOCK_EDGES = [
    {"id": "e1", "source": "fw-edge-001", "target": "srv-web-001", "type": "normal"},
    {"id": "e2", "source": "srv-web-001", "target": "srv-db-001", "type": "normal"},
    {"id": "e3", "source": "fw-edge-001", "target": "endpoint-001", "type": "normal"},
    {"id": "e4", "source": "fw-edge-001", "target": "endpoint-002", "type": "normal"},
    {"id": "e5", "source": "srv-db-001", "target": "cloud-001", "type": "warning"},
]


# ============================================
# API 端点
# ============================================

@router.get("/topology/graph")
async def get_topology_graph(
    zoom_level: Optional[float] = Query(1.0, description="缩放级别，用于节点聚合")
) -> dict:
    """获取网络拓扑图"""
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "nodes": MOCK_NODES,
            "edges": MOCK_EDGES,
            "zoom_level": zoom_level,
            "total_nodes": len(MOCK_NODES),
            "total_edges": len(MOCK_EDGES)
        }
    }


@router.get("/topology/stats")
async def get_topology_stats() -> dict:
    """获取拓扑统计信息"""
    stats = {
        "total_assets": len(MOCK_NODES),
        "by_type": {},
        "by_status": {},
        "average_risk_score": 0
    }
    
    for node in MOCK_NODES:
        # 按类型统计
        node_type = node["type"]
        stats["by_type"][node_type] = stats["by_type"].get(node_type, 0) + 1
        
        # 按状态统计
        node_status = node["status"]
        stats["by_status"][node_status] = stats["by_status"].get(node_status, 0) + 1
    
    # 计算平均风险评分
    total_risk = sum(n["risk_score"] for n in MOCK_NODES)
    stats["average_risk_score"] = total_risk / len(MOCK_NODES) if MOCK_NODES else 0
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": stats
    }
