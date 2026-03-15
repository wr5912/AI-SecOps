"""
Layer 5: 智能分析层
LLM威胁研判与智能分析

功能：
- 告警研判分析
- 事件关联分析  
- 威胁情报关联
- 智能建议生成
"""

import uuid
import json
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger

# 尝试导入LLM Provider
try:
    from backend.src.core.llm_provider import get_llm_provider, BaseLLMProvider
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("LLM Provider不可用，使用规则模拟分析")


class AnalysisType(str, Enum):
    """分析类型"""
    TRIAGE = "triage"           # 告警研判
    ROOT_CAUSE = "root_cause"   # 根因分析
    THREAT_INTEL = "threat_intel"  # 威胁情报
    RECOMMENDATION = "recommendation"  # 建议生成
    STORYLINE = "storyline"     # 故事线构建


class ThreatLevel(str, Enum):
    """威胁等级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AnalysisResult(BaseModel):
    """分析结果"""
    analysis_id: str
    alert_id: str
    analysis_type: AnalysisType
    threat_level: ThreatLevel
    summary: str
    details: Dict[str, Any]
    mitre_tactics: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class TriageResult(BaseModel):
    """研判结果"""
    is_true_positive: bool
    threat_level: ThreatLevel
    category: str
    description: str
    evidence: List[str]
    confidence: float


class PromptTemplate:
    """LLM提示词模板"""
    
    ALERT_TRIAGE_TEMPLATE = """你是一个资深安全分析师。请分析以下告警并判断是否为真实威胁。

## 告警信息
- 告警ID: {alert_id}
- 告警类型: {alert_type}
- 严重程度: {severity}
- 源IP: {source_ip}
- 目标IP: {target_ip}
- 描述: {description}
- 时间: {timestamp}

## 上下文
- 资产信息: {asset_info}
- 历史告警: {history}

请分析并返回JSON格式的研判结果：
{{
    "is_true_positive": true/false,
    "threat_level": "critical/high/medium/low",
    "category": "攻击类型分类",
    "description": "简短描述",
    "evidence": ["证据1", "证据2"],
    "confidence": 0.0-1.0
}}
"""

    ROOT_CAUSE_TEMPLATE = """你是一个安全事件调查专家。请分析以下安全事件的根本原因。

## 事件信息
- 事件ID: {event_id}
- 告警列表: {alerts}
- 涉及资产: {assets}
- 时间线: {timeline}

请分析并返回JSON格式的根因分析结果：
{{
    "root_cause": "根本原因描述",
    "attack_chain": ["步骤1", "步骤2"],
    "impact_scope": "影响范围",
    "mitre_tactics": ["T1234", "T5678"],
    "confidence": 0.0-1.0
}}
"""

    RECOMMENDATION_TEMPLATE = """你是一个安全运营顾问。基于以下分析结果，请提供安全处置建议。

## 分析结果
- 威胁类型: {threat_type}
- 严重程度: {severity}
- 涉及系统: {systems}
- 攻击者: {attackers}

## 当前状态
- 已采取措施: {actions_taken}
- 资产风险: {asset_risk}

请提供JSON格式的处置建议：
{{
    "immediate_actions": ["立即执行的操作1", "操作2"],
    "short_term_actions": ["短期建议1", "建议2"],
    "long_term_actions": ["长期改进建议1", "建议2"],
    "priority": "high/medium/low"
}}
"""


class ThreatAnalyzer:
    """威胁智能分析器"""
    
    def __init__(self):
        self.llm_provider = None
        if LLM_AVAILABLE:
            try:
                self.llm_provider = get_llm_provider()
                logger.info("LLM分析器初始化成功")
            except Exception as e:
                logger.warning(f"LLM Provider初始化失败: {e}")
        
        # 分析缓存
        self._cache: Dict[str, AnalysisResult] = {}
        
        # 初始化示例规则
        self._init_rules()
    
    def _init_rules(self):
        """初始化分析规则"""
        self.rules = {
            # 暴力破解检测
            "brute_force": {
                "keywords": ["failed", "invalid", "password", "logon", "attempt"],
                "threshold": 5,
                "time_window": 300,
                "mitre_tactics": ["T1110"]
            },
            # 恶意软件
            "malware": {
                "keywords": ["malware", "virus", "trojan", "ransomware", "payload"],
                "mitre_tactics": ["T1566", "T1204"]
            },
            # 数据外泄
            "data_exfiltration": {
                "keywords": ["exfil", "upload", "large", "outbound", "sensitive"],
                "mitre_tactics": ["T1041", "T1567"]
            },
            # 权限提升
            "privilege_escalation": {
                "keywords": ["admin", "root", "sudo", "privilege", "escalation"],
                "mitre_tactics": ["T1068", "T1548"]
            },
            # 横向移动
            "lateral_movement": {
                "keywords": ["psexec", "wmi", "winrm", "smb", "lateral"],
                "mitre_tactics": ["T1021", "T1210"]
            }
        }
    
    async def triage_alert(
        self,
        alert: Dict[str, Any]
    ) -> TriageResult:
        """告警研判"""
        alert_id = alert.get("id", "unknown")
        description = alert.get("description", "")
        severity = alert.get("severity", "medium")
        
        logger.info(f"开始研判告警: {alert_id}")
        
        # 尝试使用LLM分析
        if self.llm_provider:
            try:
                result = await self._llm_triage(alert)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"LLM研判失败，使用规则: {e}")
        
        # 回退到规则分析
        return self._rule_based_triage(alert)
    
    async def _llm_triage(self, alert: Dict[str, Any]) -> Optional[TriageResult]:
        """LLM驱动的告警研判"""
        template = PromptTemplate.ALERT_TRIAGE_TEMPLATE
        
        # 填充模板
        prompt = template.format(
            alert_id=alert.get("id", ""),
            alert_type=alert.get("type", ""),
            severity=alert.get("severity", ""),
            source_ip=alert.get("source_ip", "unknown"),
            target_ip=alert.get("target_ip", "unknown"),
            description=alert.get("description", ""),
            timestamp=alert.get("timestamp", ""),
            asset_info=json.dumps(alert.get("assets", [])),
            history=json.dumps(alert.get("recent_alerts", []))
        )
        
        # 调用LLM
        response = await self.llm_provider.chat_complete(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        # 解析JSON响应
        try:
            result = json.loads(response.content)
            return TriageResult(
                is_true_positive=result.get("is_true_positive", False),
                threat_level=ThreatLevel(result.get("threat_level", "medium")),
                category=result.get("category", "unknown"),
                description=result.get("description", ""),
                evidence=result.get("evidence", []),
                confidence=result.get("confidence", 0.5)
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"解析LLM响应失败: {e}")
            return None
    
    def _rule_based_triage(self, alert: Dict[str, Any]) -> TriageResult:
        """基于规则的告警研判"""
        description = alert.get("description", "").lower()
        severity = alert.get("severity", "medium")
        
        # 检测关键词匹配
        matched_rules = []
        for rule_name, rule in self.rules.items():
            for keyword in rule.get("keywords", []):
                if keyword.lower() in description:
                    matched_rules.append(rule_name)
                    break
        
        # 判断是否为真实威胁
        is_tp = len(matched_rules) > 0
        
        # 确定威胁等级
        if severity in ["critical", "high"]:
            threat_level = ThreatLevel.CRITICAL if is_tp else ThreatLevel.HIGH
        elif severity == "medium":
            threat_level = ThreatLevel.HIGH if is_tp else ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.MEDIUM if is_tp else ThreatLevel.LOW
        
        # 获取MITRE Tactics
        mitre = []
        for rule_name in matched_rules:
            if rule_name in self.rules:
                mitre.extend(self.rules[rule_name].get("mitre_tactics", []))
        
        return TriageResult(
            is_true_positive=is_tp,
            threat_level=threat_level,
            category=matched_rules[0] if matched_rules else "unknown",
            description=f"检测到匹配规则: {', '.join(matched_rules)}" if matched_rules else "未匹配已知攻击模式",
            evidence=[f"关键词匹配: {', '.join(matched_rules)}"] if matched_rules else [],
            confidence=0.8 if matched_rules else 0.3
        )
    
    async def analyze_root_cause(
        self,
        event_id: str,
        alerts: List[Dict[str, Any]],
        assets: List[Dict[str, Any]]
    ) -> AnalysisResult:
        """根因分析"""
        logger.info(f"开始根因分析: {event_id}")
        
        timeline = sorted(
            alerts,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        
        # 使用LLM分析
        if self.llm_provider:
            try:
                template = PromptTemplate.ROOT_CAUSE_TEMPLATE
                prompt = template.format(
                    event_id=event_id,
                    alerts=json.dumps(alerts[:10]),  # 限制数量
                    assets=json.dumps(assets[:5]),
                    timeline=json.dumps([a.get("timestamp") for a in timeline[:5]])
                )
                
                response = await self.llm_provider.chat_complete(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=1500
                )
                
                try:
                    result = json.loads(response.content)
                    return AnalysisResult(
                        analysis_id=str(uuid.uuid4()),
                        alert_id=event_id,
                        analysis_type=AnalysisType.ROOT_CAUSE,
                        threat_level=ThreatLevel(result.get("threat_level", "medium")),
                        summary=result.get("root_cause", ""),
                        details={
                            "attack_chain": result.get("attack_chain", []),
                            "impact_scope": result.get("impact_scope", "")
                        },
                        mitre_tactics=result.get("mitre_tactics", []),
                        confidence=result.get("confidence", 0.7)
                    )
                except:
                    pass
            except Exception as e:
                logger.warning(f"LLM根因分析失败: {e}")
        
        # 回退到简化分析
        return self._simple_root_cause(event_id, alerts, assets)
    
    def _simple_root_cause(
        self,
        event_id: str,
        alerts: List[Dict[str, Any]],
        assets: List[Dict[str, Any]]
    ) -> AnalysisResult:
        """简化根因分析"""
        # 提取攻击模式
        attack_patterns = set()
        for alert in alerts:
            desc = alert.get("description", "").lower()
            for rule_name, rule in self.rules.items():
                for kw in rule.get("keywords", []):
                    if kw in desc:
                        attack_patterns.add(rule_name)
        
        mitre_tactics = []
        for pattern in attack_patterns:
            if pattern in self.rules:
                mitre_tactics.extend(self.rules[pattern].get("mitre_tactics", []))
        
        return AnalysisResult(
            analysis_id=str(uuid.uuid4()),
            alert_id=event_id,
            analysis_type=AnalysisType.ROOT_CAUSE,
            threat_level=ThreatLevel.HIGH,
            summary=f"检测到{len(attack_patterns)}种攻击模式: {', '.join(attack_patterns)}",
            details={
                "attack_patterns": list(attack_patterns),
                "alert_count": len(alerts),
                "affected_assets": len(assets)
            },
            mitre_tactics=list(set(mitre_tactics)),
            confidence=0.75
        )
    
    async def generate_recommendations(
        self,
        threat_type: str,
        severity: str,
        systems: List[str],
        attackers: List[str],
        actions_taken: List[str]
    ) -> List[str]:
        """生成处置建议"""
        if self.llm_provider:
            try:
                template = PromptTemplate.RECOMMENDATION_TEMPLATE
                prompt = template.format(
                    threat_type=threat_type,
                    severity=severity,
                    systems=json.dumps(systems),
                    attackers=json.dumps(attackers),
                    actions_taken=json.dumps(actions_taken),
                    asset_risk="high" if severity == "critical" else "medium"
                )
                
                response = await self.llm_provider.chat_complete(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=1500
                )
                
                result = json.loads(response.content)
                recommendations = []
                recommendations.extend(result.get("immediate_actions", []))
                recommendations.extend(result.get("short_term_actions", []))
                recommendations.extend(result.get("long_term_actions", []))
                return recommendations[:10]  # 限制数量
            except Exception as e:
                logger.warning(f"LLM建议生成失败: {e}")
        
        # 默认建议
        return self._default_recommendations(threat_type, severity)
    
    def _default_recommendations(self, threat_type: str, severity: str) -> List[str]:
        """默认处置建议"""
        recommendations = []
        
        if severity in ["critical", "high"]:
            recommendations.extend([
                "立即隔离受影响系统",
                "阻断恶意IP/域名",
                "收集取证数据",
                "通知安全团队"
            ])
        
        if "brute_force" in threat_type:
            recommendations.extend([
                "强制重置密码",
                "启用多因素认证",
                "审查失败登录日志"
            ])
        elif "malware" in threat_type:
            recommendations.extend([
                "进行全面病毒扫描",
                "检查系统完整性",
                "更新病毒库"
            ])
        elif "lateral_movement" in threat_type:
            recommendations.extend([
                "审查网络分段",
                "检查横向移动痕迹",
                "限制内网访问"
            ])
        
        return recommendations
    
    async def correlate_threat_intel(
        self,
        indicator: str,
        indicator_type: str = "ip"
    ) -> Dict[str, Any]:
        """威胁情报关联"""
        logger.info(f"查询威胁情报: {indicator}")
        
        # 模拟威胁情报库
        threat_intel_db = {
            "203.0.113.45": {
                "malicious": True,
                "confidence": 0.95,
                "threat_actors": ["APT29", "Lazarus"],
                "campaigns": ["Operation Dream", "COVID-19 phishing"],
                "first_seen": "2024-01-15",
                "tags": ["c2", "phishing", "malware"]
            },
            "10.0.0.25": {
                "malicious": True,
                "confidence": 0.85,
                "threat_actors": [],
                "campaigns": [],
                "first_seen": "2024-02-20",
                "tags": ["compromised", "data_exfiltration"]
            }
        }
        
        result = threat_intel_db.get(indicator, {})
        
        return {
            "indicator": indicator,
            "type": indicator_type,
            "is_malicious": result.get("malicious", False),
            "confidence": result.get("confidence", 0.0),
            "threat_actors": result.get("threat_actors", []),
            "campaigns": result.get("campaigns", []),
            "tags": result.get("tags", []),
            "first_seen": result.get("first_seen"),
            "query_time": datetime.now().isoformat()
        }


# 全局实例
_analyzer: Optional[ThreatAnalyzer] = None


def get_analyzer() -> ThreatAnalyzer:
    """获取全局分析器"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ThreatAnalyzer()
    return _analyzer


# ============================================
# FastAPI 端点
# ============================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class TriageRequest(BaseModel):
    """研判请求"""
    alert: dict


class RootCauseRequest(BaseModel):
    """根因分析请求"""
    event_id: str
    alerts: List[dict]
    assets: List[dict]


class IntelRequest(BaseModel):
    """威胁情报请求"""
    indicator: str
    indicator_type: str = "ip"


@router.post("/layer5/triage")
async def triage_alert(request: TriageRequest) -> dict:
    """告警研判"""
    analyzer = get_analyzer()
    result = await analyzer.triage_alert(request.alert)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "is_true_positive": result.is_true_positive,
            "threat_level": result.threat_level.value,
            "category": result.category,
            "description": result.description,
            "evidence": result.evidence,
            "confidence": result.confidence
        }
    }


@router.post("/layer5/root-cause")
async def analyze_root_cause(request: RootCauseRequest) -> dict:
    """根因分析"""
    analyzer = get_analyzer()
    result = await analyzer.analyze_root_cause(
        request.event_id,
        request.alerts,
        request.assets
    )
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "analysis_id": result.analysis_id,
            "summary": result.summary,
            "details": result.details,
            "mitre_tactics": result.mitre_tactics,
            "confidence": result.confidence,
            "threat_level": result.threat_level.value
        }
    }


@router.post("/layer5/recommendations")
async def get_recommendations(
    threat_type: str,
    severity: str,
    systems: List[str],
    attackers: List[str] = [],
    actions_taken: List[str] = []
) -> dict:
    """获取处置建议"""
    analyzer = get_analyzer()
    recommendations = await analyzer.generate_recommendations(
        threat_type, severity, systems, attackers, actions_taken
    )
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "recommendations": recommendations
        }
    }


@router.post("/layer5/threat-intel")
async def query_threat_intel(request: IntelRequest) -> dict:
    """查询威胁情报"""
    analyzer = get_analyzer()
    intel = await analyzer.correlate_threat_intel(
        request.indicator,
        request.indicator_type
    )
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": intel
    }


@router.get("/layer5/rules")
async def get_analysis_rules() -> dict:
    """获取分析规则"""
    analyzer = get_analyzer()
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "rules": analyzer.rules
        }
    }
