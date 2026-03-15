"""
Layer 2: 数据清洗与标准化
负责将不同来源的日志转换为统一的OCSF格式
"""

import uuid
import re
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field
from loguru import logger


class EventClass(str, Enum):
    """OCSF事件类"""
    SECURITY_FINDING = "Security Finding"
    NETWORK_ACTIVITY = "Network Activity"
    FILE_ACTIVITY = "File Activity"
    PROCESS_ACTIVITY = "Process Activity"
    IDENTITY = "Identity"


class NormalizedEvent(BaseModel):
    """标准化后的事件"""
    # OCSF必需字段
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = Field(default_factory=lambda: f"trk-evt-{uuid.uuid4().hex[:8]}")
    time: datetime = Field(default_factory=datetime.utcnow)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # 事件分类
    category_uid: int = 1
    class_uid: int = 1001
    activity_id: int = 1
    
    # 来源信息
    source_name: str
    source_uid: str
    
    # 基础字段
    type_name: str
    severity_id: int = 1  # 1=Info, 2=Low, 3=Medium, 4=High, 5=Critical
    status: str = "new"
    
    # 网络字段
    src_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_ip: Optional[str] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    
    # 资产字段
    src_asset: Optional[dict] = None
    dst_asset: Optional[dict] = None
    
    # 告警字段
    alert_name: Optional[str] = None
    alert_description: Optional[str] = None
    confidence_score: Optional[int] = None
    
    # MITRE ATT&CK
    mitre_tactics: list[str] = []
    mitre_techniques: list[str] = []
    
    # 原始数据
    raw_data: dict = {}


class Normalizer:
    """
    数据清洗与标准化器
    1. 字段映射与提取
    2. OCSF格式转换
    3. 资产信息关联
    4. 威胁情报 enrichment
    """
    
    def __init__(self):
        self.stats = {
            "total_processed": 0,
            "by_source": {},
            "by_class": {}
        }
    
    async def normalize(self, raw_log: dict, source: str) -> NormalizedEvent:
        """
        标准化日志
        
        Args:
            raw_log: 原始日志
            source: 日志来源
            
        Returns:
            标准化后的事件
        """
        self.stats["total_processed"] += 1
        
        if source not in self.stats["by_source"]:
            self.stats["by_source"][source] = 0
        self.stats["by_source"][source] += 1
        
        # 根据来源选择不同的标准化策略
        if source == "suricata":
            return await self._normalize_suricata(raw_log)
        elif source == "sangfor":
            return await self._normalize_sangfor(raw_log)
        elif source == "waf":
            return await self._normalize_waf(raw_log)
        else:
            return await self._normalize_generic(raw_log, source)
    
    async def _normalize_suricata(self, raw_log: dict) -> NormalizedEvent:
        """标准化Suricata日志"""
        # 提取字段
        alert = raw_log.get("alert", {})
        
        event = NormalizedEvent(
            source_name="suricata",
            source_uid="suricata-001",
            type_name=alert.get("signature", "Unknown"),
            severity_id=self._map_suricata_severity(alert.get("severity", 1)),
            src_ip=raw_log.get("src_ip"),
            src_port=raw_log.get("src_port"),
            dst_ip=raw_log.get("dest_ip"),
            dst_port=raw_log.get("dest_port"),
            protocol=raw_log.get("proto"),
            alert_name=alert.get("signature"),
            alert_description=alert.get("signature_id"),
            raw_data=raw_log
        )
        
        # MITRE映射
        if "signature" in raw_log:
            mitre = self._map_signature_to_mitre(raw_log["signature"])
            event.mitre_tactics = mitre["tactics"]
            event.mitre_techniques = mitre["techniques"]
        
        self._update_class_stats(event.class_uid)
        return event
    
    async def _normalize_sangfor(self, raw_log: dict) -> NormalizedEvent:
        """标准化Sangfor日志"""
        event = NormalizedEvent(
            source_name="sangfor",
            source_uid="sangfor-001",
            type_name=raw_log.get("event_type", "Unknown"),
            severity_id=self._map_sangfor_severity(raw_log.get("risk_level", 1)),
            src_ip=raw_log.get("src_ip"),
            src_port=raw_log.get("src_port"),
            dst_ip=raw_log.get("dst_ip"),
            dst_port=raw_log.get("dst_port"),
            alert_name=raw_log.get("event_name"),
            alert_description=raw_log.get("description"),
            raw_data=raw_log
        )
        
        self._update_class_stats(event.class_uid)
        return event
    
    async def _normalize_waf(self, raw_log: dict) -> NormalizedEvent:
        """标准化WAF日志"""
        event = NormalizedEvent(
            source_name="waf",
            source_uid="waf-001",
            type_name=raw_log.get("rule_name", "Unknown"),
            severity_id=4,  # WAF告警通常较高
            src_ip=raw_log.get("client_ip"),
            src_port=raw_log.get("client_port"),
            dst_ip=raw_log.get("server_ip"),
            dst_port=raw_log.get("server_port"),
            alert_name=raw_log.get("rule_name"),
            alert_description=raw_log.get("attack_type"),
            raw_data=raw_log
        )
        
        # WAF常见攻击类型映射
        attack_type = raw_log.get("attack_type", "").lower()
        if "sql" in attack_type or "sqli" in attack_type:
            event.mitre_tactics = ["TA0010"]
            event.mitre_techniques = ["T1190"]
        elif "xss" in attack_type:
            event.mitre_tactics = ["TA0010"]
            event.mitre_techniques = ["T1189"]
        
        self._update_class_stats(event.class_uid)
        return event
    
    async def _normalize_generic(self, raw_log: dict, source: str) -> NormalizedEvent:
        """通用标准化"""
        # 尝试智能提取IP字段
        src_ip = raw_log.get("src_ip") or raw_log.get("source_ip") or raw_log.get("client_ip")
        dst_ip = raw_log.get("dst_ip") or raw_log.get("dest_ip") or raw_log.get("server_ip")
        
        event = NormalizedEvent(
            source_name=source,
            source_uid=f"{source}-001",
            type_name=raw_log.get("type", raw_log.get("event_type", "Unknown")),
            severity_id=raw_log.get("severity", 1),
            src_ip=src_ip,
            src_port=raw_log.get("src_port") or raw_log.get("source_port"),
            dst_ip=dst_ip,
            dst_port=raw_log.get("dst_port") or raw_log.get("dest_port"),
            protocol=raw_log.get("protocol") or raw_log.get("proto"),
            alert_name=raw_log.get("alert") or raw_log.get("message"),
            raw_data=raw_log
        )
        
        self._update_class_stats(event.class_uid)
        return event
    
    def _map_suricata_severity(self, severity: int) -> int:
        """映射Suricata严重级别到OCSF"""
        mapping = {
            1: 1,  # Low -> Info
            2: 2,  # Medium -> Low
            3: 3,  # High -> Medium
        }
        return mapping.get(severity, 2)
    
    def _map_sangfor_severity(self, level: int) -> int:
        """映射Sangfor风险级别"""
        mapping = {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
        }
        return mapping.get(level, 2)
    
    def _map_signature_to_mitre(self, signature: str) -> dict:
        """将签名映射到MITRE ATT&CK"""
        sig_lower = signature.lower()
        
        mappings = {
            "et exploit": {"tactics": ["TA0001"], "techniques": ["T1190"]},
            "et malware": {"tactics": ["TA0042"], "techniques": ["T1059"]},
            "et c2": {"tactics": ["TA0011"], "techniques": ["T1071"]},
            "et scanning": {"tactics": ["TA0043"], "techniques": ["T1595"]},
        }
        
        for keyword, mitre in mappings.items():
            if keyword in sig_lower:
                return mitre
        
        return {"tactics": [], "techniques": []}
    
    def _update_class_stats(self, class_uid: int):
        """更新分类统计"""
        if class_uid not in self.stats["by_class"]:
            self.stats["by_class"][class_uid] = 0
        self.stats["by_class"][class_uid] += 1
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats


# 全局实例
normalizer = Normalizer()


# ============================================
# API 端点
# ============================================

from fastapi import APIRouter

router = APIRouter()


@router.post("/layer2/normalize")
async def normalize_log(log: dict, source: str) -> dict:
    """
    标准化单条日志
    """
    event = await normalizer.normalize(log, source)
    return {
        "trace_id": event.trace_id,
        "success": True,
        "data": event.model_dump()
    }


@router.post("/layer2/normalize/batch")
async def normalize_logs_batch(logs: list[dict], source: str) -> dict:
    """
    批量标准化日志
    """
    results = []
    for log in logs:
        event = await normalizer.normalize(log, source)
        results.append(event.model_dump())
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "total": len(results),
        "data": results
    }


@router.get("/layer2/stats")
async def get_normalizer_stats() -> dict:
    """
    获取标准化统计
    """
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": normalizer.get_stats()
    }
