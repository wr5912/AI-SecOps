"""
资产API路由
"""

import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


# ============================================
# Pydantic 模型
# ============================================

class AssetStatus(str):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    COMPROMISED = "compromised"


class AssetType(str):
    SERVER = "server"
    ENDPOINT = "endpoint"
    DATABASE = "database"
    FIREWALL = "firewall"
    IOT = "iot"
    CLOUD = "cloud"


class AssetResponse(BaseModel):
    """资产响应"""
    id: str
    trace_id: str
    name: str
    ip: str
    type: str
    status: str
    risk_score: int
    os: str
    department: str
    owner: str
    ports: list[int] = []
    vulnerabilities: list[dict] = []
    connections: list[str] = []


class AssetHologramResponse(BaseModel):
    """资产360度全息卡片响应"""
    asset: AssetResponse
    related_assets: list[AssetResponse]
    recent_alerts: list[dict]
    network_connections: list[dict]


class AssetActionRequest(BaseModel):
    """资产操作请求"""
    action: str
    parameters: dict = {}


# ============================================
# 模拟数据
# ============================================

MOCK_ASSETS = [
    {
        "id": "srv-web-001",
        "trace_id": "trk-asset-001",
        "name": "Web服务器-01",
        "ip": "192.168.1.10",
        "type": "server",
        "status": "normal",
        "risk_score": 25,
        "os": "Ubuntu 22.04",
        "department": "信息技术部",
        "owner": "张三",
        "ports": [80, 443, 22],
        "vulnerabilities": [{"cvss": 5.3, "name": "CVE-2024-1234"}],
        "connections": ["srv-db-001", "fw-edge-001"]
    },
    {
        "id": "srv-db-001",
        "trace_id": "trk-asset-002",
        "name": "数据库服务器-01",
        "ip": "192.168.1.20",
        "type": "database",
        "status": "warning",
        "risk_score": 65,
        "os": "CentOS 8",
        "department": "信息技术部",
        "owner": "李四",
        "ports": [3306, 22],
        "vulnerabilities": [{"cvss": 7.5, "name": "CVE-2024-5678"}],
        "connections": ["srv-web-001"]
    },
    {
        "id": "fw-edge-001",
        "trace_id": "trk-asset-003",
        "name": "边界防火墙",
        "ip": "192.168.1.1",
        "type": "firewall",
        "status": "normal",
        "risk_score": 10,
        "os": "FortiOS 7.0",
        "department": "安全运营部",
        "owner": "王五",
        "ports": [443, 22],
        "vulnerabilities": [],
        "connections": ["srv-web-001", "endpoint-001"]
    },
    {
        "id": "endpoint-001",
        "trace_id": "trk-asset-004",
        "name": "员工终端-01",
        "ip": "192.168.1.100",
        "type": "endpoint",
        "status": "critical",
        "risk_score": 85,
        "os": "Windows 11",
        "department": "市场部",
        "owner": "赵六",
        "ports": [],
        "vulnerabilities": [{"cvss": 9.8, "name": "CVE-2024-9999"}],
        "connections": ["fw-edge-001"]
    },
]


# ============================================
# API 端点
# ============================================

@router.get("/assets")
async def list_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
) -> dict:
    """获取资产列表"""
    filtered_assets = MOCK_ASSETS
    
    if status:
        filtered_assets = [a for a in filtered_assets if a["status"] == status]
    if asset_type:
        filtered_assets = [a for a in filtered_assets if a["type"] == asset_type]
    
    total = len(filtered_assets)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered_assets[start:end]
    
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


@router.get("/assets/{asset_id}")
async def get_asset(asset_id: str) -> dict:
    """获取单个资产详情"""
    asset = next((a for a in MOCK_ASSETS if a["id"] == asset_id), None)
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": asset
    }


@router.get("/assets/{asset_id}/hologram")
async def get_asset_hologram(asset_id: str) -> dict:
    """获取资产360度全息卡片"""
    asset = next((a for a in MOCK_ASSETS if a["id"] == asset_id), None)
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # 获取关联资产
    related_assets = [
        a for a in MOCK_ASSETS 
        if a["id"] in asset["connections"]
    ]
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "asset": asset,
            "related_assets": related_assets,
            "recent_alerts": [
                {
                    "id": "alert-001",
                    "severity": "high",
                    "time": "2026-03-14T10:00:00Z",
                    "description": "检测到可疑连接"
                }
            ],
            "network_connections": []
        }
    }


@router.post("/assets/{asset_id}/actions")
async def execute_asset_action(
    asset_id: str,
    action: AssetActionRequest
) -> dict:
    """执行资产操作"""
    asset = next((a for a in MOCK_ASSETS if a["id"] == asset_id), None)
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # 记录操作
    print(f"执行资产操作: {asset_id} - {action.action} - {action.parameters}")
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "asset_id": asset_id,
            "action": action.action,
            "status": "executed",
            "result": "操作已提交执行"
        }
    }
