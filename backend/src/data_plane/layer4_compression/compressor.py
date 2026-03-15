"""
Layer 4: 告警压缩与归并
负责告警去重、归并、关联分析，生成高级告警
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from collections import defaultdict
from pydantic import BaseModel, Field
from loguru import logger


class AlertGroup(BaseModel):
    """告警组"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = Field(default_factory=lambda: f"trk-group-{uuid.uuid4().hex[:8]}")
    name: str
    description: str
    alert_count: int = 0
    severity: str = "medium"
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    alerts: List[str] = []  # 告警ID列表
    attack_indicators: List[str] = []
    mitre_tactics: List[str] = []
    status: str = "active"


class AlertCompressor:
    """
    告警压缩与归并器
    1. 告警去重
    2. 相似告警归并
    3. 攻击链关联
    4. 高级告警生成
    """
    
    def __init__(
        self,
        dedup_window_seconds: int = 300,
        similarity_threshold: float = 0.8
    ):
        """
        初始化压缩器
        
        Args:
            dedup_window_seconds: 去重时间窗口（秒）
            similarity_threshold: 相似度阈值
        """
        self.dedup_window = timedelta(seconds=dedup_window_seconds)
        self.similarity_threshold = similarity_threshold
        
        # 告警缓存（用于去重）
        self.alert_cache: Dict[str, datetime] = {}
        
        # 活跃告警组
        self.alert_groups: Dict[str, AlertGroup] = {}
        
        # 统计
        self.stats = {
            "total_processed": 0,
            "deduplicated": 0,
            "merged": 0,
            "new_groups": 0
        }
    
    async def process_alert(self, alert: dict) -> dict:
        """
        处理告警
        
        Args:
            alert: 标准化后的告警
            
        Returns:
            处理结果
        """
        self.stats["total_processed"] += 1
        
        alert_id = alert.get("id", str(uuid.uuid4()))
        alert_timestamp = datetime.fromisoformat(
            alert.get("timestamp", datetime.utcnow().isoformat())
        )
        
        # 1. 去重检查
        dedup_key = self._generate_dedup_key(alert)
        if self._is_duplicate(dedup_key, alert_timestamp):
            self.stats["deduplicated"] += 1
            logger.debug(f"Alert deduplicated: {alert_id}")
            return {
                "action": "deduplicated",
                "alert_id": alert_id
            }
        
        # 2. 查找匹配的告警组
        matched_group = await self._find_matching_group(alert)
        
        if matched_group:
            # 3. 加入现有组
            await self._add_to_group(matched_group, alert)
            self.stats["merged"] += 1
            return {
                "action": "merged",
                "alert_id": alert_id,
                "group_id": matched_group.id
            }
        else:
            # 4. 创建新告警组
            new_group = await self._create_new_group(alert)
            self.stats["new_groups"] += 1
            return {
                "action": "new_group",
                "alert_id": alert_id,
                "group_id": new_group.id
            }
    
    def _generate_dedup_key(self, alert: dict) -> str:
        """生成去重键"""
        # 基于关键字段生成唯一键
        src_ip = alert.get("src_ip", "")
        dst_ip = alert.get("dst_ip", "")
        alert_name = alert.get("alert_name", alert.get("type_name", ""))
        
        return f"{src_ip}:{dst_ip}:{alert_name}"
    
    def _is_duplicate(self, dedup_key: str, timestamp: datetime) -> bool:
        """检查是否重复"""
        if dedup_key in self.alert_cache:
            last_seen = self.alert_cache[dedup_key]
            if timestamp - last_seen < self.dedup_window:
                return True
        
        # 更新缓存
        self.alert_cache[dedup_key] = timestamp
        
        # 清理过期缓存
        self._cleanup_cache(timestamp)
        
        return False
    
    def _cleanup_cache(self, current_time: datetime):
        """清理过期缓存"""
        expire_time = current_time - timedelta(seconds=self.dedup_window.total_seconds() * 2)
        expired_keys = [
            k for k, v in self.alert_cache.items()
            if v < expire_time
        ]
        for k in expired_keys:
            del self.alert_cache[k]
    
    async def _find_matching_group(self, alert: dict) -> Optional[AlertGroup]:
        """查找匹配的告警组"""
        src_ip = alert.get("src_ip")
        dst_ip = alert.get("dst_ip")
        alert_name = alert.get("alert_name", "")
        
        for group in self.alert_groups.values():
            if group.status != "active":
                continue
            
            # 检查时间窗口
            time_diff = datetime.utcnow() - group.last_seen
            if time_diff > timedelta(hours=24):  # 超过24小时的组不匹配
                continue
            
            # 检查IP匹配
            for indicator in group.attack_indicators:
                if src_ip == indicator or dst_ip == indicator:
                    return group
                
                # 检查同一网段
                if src_ip and src_ip.startswith(indicator.rsplit(".", 1)[0]):
                    return group
        
        return None
    
    async def _create_new_group(self, alert: dict) -> AlertGroup:
        """创建新告警组"""
        alert_name = alert.get("alert_name", alert.get("type_name", "Unknown"))
        
        group = AlertGroup(
            name=f"Alert Group: {alert_name}",
            description=f"Group of related alerts for {alert_name}",
            severity=alert.get("severity_id", 2),
            alerts=[alert.get("id", str(uuid.uuid4()))]
        )
        
        # 添加攻击指标
        if alert.get("src_ip"):
            group.attack_indicators.append(alert["src_ip"])
        if alert.get("dst_ip"):
            group.attack_indicators.append(alert["dst_ip"])
        
        # 添加MITRE战术
        if alert.get("mitre_tactics"):
            group.mitre_tactics = alert["mitre_tactics"]
        
        self.alert_groups[group.id] = group
        logger.info(f"Created new alert group: {group.id}")
        
        return group
    
    async def _add_to_group(self, group: AlertGroup, alert: dict):
        """向告警组添加告警"""
        alert_id = alert.get("id", str(uuid.uuid4()))
        
        if alert_id not in group.alerts:
            group.alerts.append(alert_id)
            group.alert_count = len(group.alerts)
            group.last_seen = datetime.utcnow()
            
            # 更新攻击指标
            if alert.get("src_ip") and alert["src_ip"] not in group.attack_indicators:
                group.attack_indicators.append(alert["src_ip"])
            if alert.get("dst_ip") and alert["dst_ip"] not in group.attack_indicators:
                group.attack_indicators.append(alert["dst_ip"])
            
            # 更新MITRE战术
            if alert.get("mitre_tactics"):
                for tactic in alert["mitre_tactics"]:
                    if tactic not in group.mitre_tactics:
                        group.mitre_tactics.append(tactic)
            
            # 更新严重级别
            if alert.get("severity_id", 1) > int(group.severity or 1):
                group.severity = str(alert["severity_id"])
    
    async def get_group(self, group_id: str) -> Optional[AlertGroup]:
        """获取告警组"""
        return self.alert_groups.get(group_id)
    
    async def get_active_groups(self) -> List[AlertGroup]:
        """获取活跃告警组"""
        return [g for g in self.alert_groups.values() if g.status == "active"]
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            "active_groups": len([g for g in self.alert_groups.values() if g.status == "active"]),
            "compression_ratio": (
                self.stats["deduplicated"] / self.stats["total_processed"]
                if self.stats["total_processed"] > 0 else 0
            )
        }


# 全局实例
alert_compressor = AlertCompressor()


# ============================================
# API 端点
# ============================================

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/layer4/process")
async def process_alert(alert: dict) -> dict:
    """处理告警"""
    result = await alert_compressor.process_alert(alert)
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": result
    }


@router.post("/layer4/process/batch")
async def process_alerts_batch(alerts: list[dict]) -> dict:
    """批量处理告警"""
    results = []
    for alert in alerts:
        result = await alert_compressor.process_alert(alert)
        results.append(result)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "total": len(alerts),
        "results": results
    }


@router.get("/layer4/groups")
async def list_groups() -> dict:
    """列出告警组"""
    groups = list(alert_compressor.alert_groups.values())
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "items": [g.model_dump() for g in groups],
            "total": len(groups)
        }
    }


@router.get("/layer4/groups/active")
async def get_active_groups() -> dict:
    """获取活跃告警组"""
    groups = await alert_compressor.get_active_groups()
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "items": [g.model_dump() for g in groups],
            "total": len(groups)
        }
    }


@router.get("/layer4/groups/{group_id}")
async def get_group(group_id: str) -> dict:
    """获取告警组详情"""
    group = await alert_compressor.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": group.model_dump()
    }


@router.get("/layer4/stats")
async def get_compression_stats() -> dict:
    """获取压缩统计"""
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": alert_compressor.get_stats()
    }
