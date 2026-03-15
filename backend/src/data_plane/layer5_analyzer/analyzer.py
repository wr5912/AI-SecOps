"""
Layer 5: 智能分析层
负责AI驱动的威胁分析、攻击链推理、风险评估
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from pydantic import BaseModel, Field
from loguru import logger


class AnalysisType(str, Enum):
    """分析类型"""
    THREAT_INTELLIGENCE = "threat_intelligence"
    ATTACK_CHAIN = "attack_chain"
    RISK_ASSESSMENT = "risk_assessment"
    ANOMALY_DETECTION = "anomaly_detection"
    ROOT_CAUSE = "root_cause"


class AnalysisResult(BaseModel):
    """分析结果"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = Field(default_factory=lambda: f"trk-analysis-{uuid.uuid4().hex[:8]}")
    analysis_type: AnalysisType
    target_id: str
    target_type: str
    result: dict
    confidence_score: int = 50
    recommendations: List[str] = []
    mitre_tactics: List[str] = []
    mitre_techniques: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SecurityAnalyzer:
    """
    智能安全分析器
    1. 威胁情报关联分析
    2. 攻击链推理
    3. 风险评估
    4. 异常检测
    5. 根因分析
    """
    
    def __init__(self):
        self.analysis_history: Dict[str, AnalysisResult] = {}
        self.stats = {
            "total_analyses": 0,
            "by_type": {},
            "average_confidence": 0
        }
    
    async def analyze(
        self,
        analysis_type: AnalysisType,
        target_id: str,
        target_type: str,
        data: dict
    ) -> AnalysisResult:
        """
        执行分析
        
        Args:
            analysis_type: 分析类型
            target_id: 目标ID
            target_type: 目标类型
            data: 分析数据
            
        Returns:
            分析结果
        """
        self.stats["total_analyses"] += 1
        
        if analysis_type.value not in self.stats["by_type"]:
            self.stats["by_type"][analysis_type.value] = 0
        self.stats["by_type"][analysis_type.value] += 1
        
        # 根据分析类型执行不同的分析
        if analysis_type == AnalysisType.THREAT_INTELLIGENCE:
            result = await self._analyze_threat_intelligence(data)
        elif analysis_type == AnalysisType.ATTACK_CHAIN:
            result = await self._analyze_attack_chain(data)
        elif analysis_type == AnalysisType.RISK_ASSESSMENT:
            result = await self._analyze_risk(data)
        elif analysis_type == AnalysisType.ANOMALY_DETECTION:
            result = await self._analyze_anomaly(data)
        elif analysis_type == AnalysisType.ROOT_CAUSE:
            result = await self._analyze_root_cause(data)
        else:
            result = {"summary": "Unknown analysis type"}
        
        analysis = AnalysisResult(
            analysis_type=analysis_type,
            target_id=target_id,
            target_type=target_type,
            result=result
        )
        
        self.analysis_history[analysis.id] = analysis
        return analysis
    
    async def _analyze_threat_intelligence(self, data: dict) -> dict:
        """威胁情报分析"""
        ip = data.get("src_ip") or data.get("dst_ip")
        
        # 模拟IOC查询
        ioc_analysis = {
            "ip": ip,
            "reputation": "suspicious" if ip else "unknown",
            "threat_indicators": [],
            "related_campaigns": [],
            "confidence": 75
        }
        
        if ip:
            # 常见恶意IP模式
            if ip.startswith("10.0.0."):
                ioc_analysis["threat_indicators"].append("internal_scanning")
                ioc_analysis["reputation"] = "malicious"
                ioc_analysis["confidence"] = 90
        
        return {
            "type": "threat_intelligence",
            "ioc": ioc_analysis,
            "summary": f"IP {ip} reputation analysis completed"
        }
    
    async def _analyze_attack_chain(self, data: dict) -> dict:
        """攻击链分析"""
        mitre_tactics = data.get("mitre_tactics", [])
        mitre_techniques = data.get("mitre_techniques", [])
        
        # 识别攻击阶段
        attack_stages = []
        
        # MITRE ATT&CK 战术顺序
        tactic_order = [
            "TA0001",  # Initial Access
            "TA0002",  # Execution
            "TA0003",  # Persistence
            "TA0004",  # Privilege Escalation
            "TA0005",  # Defense Evasion
            "TA0006",  # Credential Access
            "TA0007",  # Discovery
            "TA0008",  # Lateral Movement
            "TA0009",  # Collection
            "TA0010",  # Exfiltration
            "TA0011",  # Command and Control
        ]
        
        sorted_tactics = sorted(
            mitre_tactics,
            key=lambda t: tactic_order.index(t) if t in tactic_order else 999
        )
        
        for i, tactic in enumerate(sorted_tactics):
            attack_stages.append({
                "stage": i + 1,
                "tactic": tactic,
                "description": self._get_tactic_description(tactic),
                "detected": True
            })
        
        # 评估攻击链完整性
        chain_completeness = len(mitre_tactics) / len(tactic_order) * 100
        
        return {
            "type": "attack_chain",
            "stages": attack_stages,
            "chain_completeness": chain_completeness,
            "risk_level": "high" if chain_completeness > 50 else "medium",
            "summary": f"Attack chain analysis: {len(attack_stages)} stages identified"
        }
    
    async def _analyze_risk(self, data: dict) -> dict:
        """风险评估"""
        severity = data.get("severity_id", 1)
        asset_criticality = data.get("asset_criticality", "medium")
        
        # 风险矩阵
        risk_matrix = {
            ("5", "critical"): 95,
            ("5", "high"): 85,
            ("5", "medium"): 70,
            ("4", "critical"): 85,
            ("4", "high"): 70,
            ("4", "medium"): 55,
            ("3", "critical"): 70,
            ("3", "high"): 55,
            ("3", "medium"): 40,
        }
        
        risk_score = risk_matrix.get(
            (str(severity), asset_criticality),
            30
        )
        
        risk_level = "critical" if risk_score > 80 else "high" if risk_score > 60 else "medium" if risk_score > 40 else "low"
        
        return {
            "type": "risk_assessment",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "factors": {
                "severity": severity,
                "asset_criticality": asset_criticality
            },
            "summary": f"Risk score: {risk_score}/100 ({risk_level})"
        }
    
    async def _analyze_anomaly(self, data: dict) -> dict:
        """异常检测"""
        # 简化的异常检测
        baseline = data.get("baseline", {})
        current = data.get("current", {})
        
        anomalies = []
        
        for key in current:
            if key in baseline:
                diff = abs(current[key] - baseline[key])
                if diff > baseline[key] * 0.5:  # 50%偏差
                    anomalies.append({
                        "metric": key,
                        "baseline": baseline[key],
                        "current": current[key],
                        "deviation": diff
                    })
        
        return {
            "type": "anomaly_detection",
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "summary": f"Detected {len(anomalies)} anomalies"
        }
    
    async def _analyze_root_cause(self, data: dict) -> dict:
        """根因分析"""
        symptoms = data.get("symptoms", [])
        
        # 简化的根因分析
        root_causes = []
        
        for symptom in symptoms:
            if "connection" in symptom.lower():
                root_causes.append({
                    "cause": "Network communication anomaly",
                    "confidence": 70,
                    "related_indicators": ["unusual_port", "unexpected_ip"]
                })
            elif "authentication" in symptom.lower():
                root_causes.append({
                    "cause": "Authentication failure",
                    "confidence": 80,
                    "related_indicators": ["failed_login", "brute_force"]
                })
        
        return {
            "type": "root_cause_analysis",
            "root_causes": root_causes,
            "summary": f"Identified {len(root_causes)} potential root causes"
        }
    
    def _get_tactic_description(self, tactic: str) -> str:
        """获取战术描述"""
        descriptions = {
            "TA0001": "Initial Access - 初始访问",
            "TA0002": "Execution - 执行",
            "TA0003": "Persistence - 持久化",
            "TA0004": "Privilege Escalation - 权限提升",
            "TA0005": "Defense Evasion - 防御规避",
            "TA0006": "Credential Access - 凭证访问",
            "TA0007": "Discovery - Discovery",
            "TA0008": "Lateral Movement - 横向移动",
            "TA0009": "Collection - 收集",
            "TA0010": "Exfiltration - 数据泄露",
            "TA0011": "Command and Control - 命令控制",
        }
        return descriptions.get(tactic, tactic)
    
    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisResult]:
        """获取分析结果"""
        return self.analysis_history.get(analysis_id)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats


# 全局实例
analyzer = SecurityAnalyzer()


# ============================================
# API 端点
# ============================================

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/layer5/analyze")
async def analyze(
    analysis_type: AnalysisType,
    target_id: str,
    target_type: str,
    data: dict
) -> dict:
    """执行分析"""
    result = await analyzer.analyze(analysis_type, target_id, target_type, data)
    return {
        "trace_id": result.trace_id,
        "success": True,
        "data": result.model_dump()
    }


@router.get("/layer5/analyses")
async def list_analyses() -> dict:
    """列出分析历史"""
    analyses = list(analyzer.analysis_history.values())
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "items": [a.model_dump() for a in analyses],
            "total": len(analyses)
        }
    }


@router.get("/layer5/analyses/{analysis_id}")
async def get_analysis(analysis_id: str) -> dict:
    """获取分析结果"""
    analysis = await analyzer.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": analysis.model_dump()
    }


@router.get("/layer5/stats")
async def get_analyzer_stats() -> dict:
    """获取分析器统计"""
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": analyzer.get_stats()
    }
