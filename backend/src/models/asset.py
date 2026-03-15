"""
资产数据模型
与前端TypeScript模型完全对齐
"""
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class AssetType(str, Enum):
    """资产类型枚举"""
    SERVER = "server"
    ENDPOINT = "endpoint"
    DATABASE = "database"
    FIREWALL = "firewall"
    IOT = "iot"
    CLOUD = "cloud"


class AssetStatus(str, Enum):
    """资产状态枚举"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    COMPROMISED = "compromised"


class AssetVulnerability(BaseModel):
    """资产漏洞"""
    cvss: float
    name: str


class Asset(BaseModel):
    """资产模型 - 与前端完全对齐"""
    id: str
    trace_id: str
    name: str
    ip: str
    type: AssetType
    status: AssetStatus
    risk_score: int
    os: str
    department: str
    owner: str
    ports: List[int] = []
    vulnerabilities: List[AssetVulnerability] = []
    connections: List[str] = []
    lastSeen: Optional[str] = None


class AssetListResponse(BaseModel):
    """资产列表响应"""
    total: int
    page: int
    page_size: int
    items: List[Asset]


class AssetHologramResponse(BaseModel):
    """资产360度全息卡片响应"""
    asset: Asset
    related_assets: List[Asset]
    recent_alerts: List[dict]
    network_connections: List[dict]
