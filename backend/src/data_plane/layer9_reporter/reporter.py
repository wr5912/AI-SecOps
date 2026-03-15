"""
Layer 9: 报告生成层
审计合规与报表生成

功能：
- 安全运营报告
- 合规审计报告
- 威胁态势分析
- 自定义报表生成
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
import json
from pydantic import BaseModel


class ReportType(str, Enum):
    """报告类型"""
    DAILY = "daily"           # 日报
    WEEKLY = "weekly"         # 周报
    MONTHLY = "monthly"       # 月报
    INCIDENT = "incident"     # 事件报告
    COMPLIANCE = "compliance" # 合规报告
    THREAT_INTEL = "threat_intel"  # 威胁情报报告
    EXECUTIVE = "executive"   # 高管简报


class ReportFormat(str, Enum):
    """报告格式"""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    CSV = "csv"


class ReportSection(BaseModel):
    """报告章节"""
    title: str
    content: Dict[str, Any]
    order: int


class Report(BaseModel):
    """报告"""
    id: str
    title: str
    report_type: ReportType
    period_start: datetime
    period_end: datetime
    sections: List[ReportSection]
    metadata: Dict[str, Any]
    created_at: str
    format: ReportFormat = ReportFormat.JSON


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        # 模拟数据存储
        self._alerts: List[Dict] = []
        self._incidents: List[Dict] = []
        self._actions: List[Dict] = []
        self._assets: List[Dict] = []
        
        # 初始化示例数据
        self._init_sample_data()
    
    def _init_sample_data(self):
        """初始化示例数据"""
        # 示例告警
        self._alerts = [
            {"id": "alert-1", "type": "brute_force", "severity": "critical", "timestamp": "2026-03-15T08:00:00Z", "source_ip": "203.0.113.45", "status": "investigating"},
            {"id": "alert-2", "type": "malware", "severity": "high", "timestamp": "2026-03-15T07:30:00Z", "source_ip": "10.0.1.100", "status": "mitigated"},
            {"id": "alert-3", "type": "phishing", "severity": "medium", "timestamp": "2026-03-15T06:00:00Z", "source_ip": "192.168.1.50", "status": "resolved"},
            {"id": "alert-4", "type": "data_exfiltration", "severity": "critical", "timestamp": "2026-03-14T22:00:00Z", "source_ip": "10.0.2.30", "status": "investigating"},
            {"id": "alert-5", "type": "unauthorized_access", "severity": "high", "timestamp": "2026-03-14T18:00:00Z", "source_ip": "203.0.113.100", "status": "mitigated"},
        ]
        
        # 示例事件
        self._incidents = [
            {"id": "inc-1", "title": "勒索软件攻击", "severity": "critical", "status": "active", "created_at": "2026-03-15T08:00:00Z", "affected_assets": 3},
            {"id": "inc-2", "title": "凭证泄露事件", "severity": "high", "status": "contained", "created_at": "2026-03-14T15:00:00Z", "affected_assets": 1},
        ]
        
        # 示例操作
        self._actions = [
            {"id": "action-1", "type": "block_ip", "target": "203.0.113.45", "status": "success", "timestamp": "2026-03-15T08:05:00Z"},
            {"id": "action-2", "type": "quarantine", "target": "ep-finance-01", "status": "success", "timestamp": "2026-03-15T08:10:00Z"},
            {"id": "action-3", "type": "notify", "target": "security_team", "status": "success", "timestamp": "2026-03-15T08:15:00Z"},
        ]
        
        # 示例资产
        self._assets = [
            {"id": "srv-web-01", "name": "Web服务器", "risk_score": 85, "status": "warning"},
            {"id": "srv-db-01", "name": "数据库服务器", "risk_score": 72, "status": "normal"},
            {"id": "ep-finance-01", "name": "财务工作站", "risk_score": 98, "status": "critical"},
        ]
    
    def generate_report(
        self,
        report_type: ReportType,
        period_start: datetime = None,
        period_end: datetime = None,
        format: ReportFormat = ReportFormat.JSON
    ) -> Report:
        """生成报告"""
        period_end = period_end or datetime.now()
        period_start = period_start or period_end - timedelta(days=1)
        
        logger.info(f"📊 生成报告: {report_type.value}")
        
        sections = []
        
        if report_type == ReportType.DAILY:
            sections = self._generate_daily_report(period_start, period_end)
        elif report_type == ReportType.WEEKLY:
            sections = self._generate_weekly_report(period_start, period_end)
        elif report_type == ReportType.MONTHLY:
            sections = self._generate_monthly_report(period_start, period_end)
        elif report_type == ReportType.INCIDENT:
            sections = self._generate_incident_report(period_start, period_end)
        elif report_type == ReportType.COMPLIANCE:
            sections = self._generate_compliance_report(period_start, period_end)
        elif report_type == ReportType.EXECUTIVE:
            sections = self._generate_executive_report(period_start, period_end)
        else:
            sections = self._generate_daily_report(period_start, period_end)
        
        # 计算元数据
        total_alerts = len(self._alerts)
        critical_alerts = len([a for a in self._alerts if a.get("severity") == "critical"])
        
        report = Report(
            id=str(uuid.uuid4()),
            title=self._get_report_title(report_type, period_start, period_end),
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            sections=sections,
            metadata={
                "total_alerts": total_alerts,
                "critical_alerts": critical_alerts,
                "open_incidents": len([i for i in self._incidents if i.get("status") == "active"]),
                "actions_taken": len(self._actions)
            },
            created_at=datetime.now().isoformat(),
            format=format
        )
        
        logger.info(f"✅ 报告生成完成: {report.id}")
        
        return report
    
    def _generate_daily_report(
        self,
        start: datetime,
        end: datetime
    ) -> List[ReportSection]:
        """生成日报"""
        sections = []
        
        # 执行摘要
        sections.append(ReportSection(
            title="执行摘要",
            content={
                "overview": "今日安全运营总体平稳，检测到5条告警，其中2条高危告警已处置",
                "key_events": [
                    "检测到暴力破解攻击，已封禁攻击源IP",
                    "财务工作站存在异常行为，已隔离"
                ],
                "risk_level": "medium"
            },
            order=1
        ))
        
        # 告警统计
        severity_counts = {}
        for alert in self._alerts:
            sev = alert.get("severity", "unknown")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        sections.append(ReportSection(
            title="告警统计",
            content={
                "total": len(self._alerts),
                "by_severity": severity_counts,
                "by_type": self._get_type_counts(self._alerts),
                "resolved": len([a for a in self._alerts if a.get("status") == "resolved"])
            },
            order=2
        ))
        
        # 事件概览
        sections.append(ReportSection(
            title="安全事件",
            content={
                "total": len(self._incidents),
                "active": len([i for i in self._incidents if i.get("status") == "active"]),
                "contained": len([i for i in self._incidents if i.get("status") == "contained"]),
                "incidents": self._incidents
            },
            order=3
        ))
        
        # 响应操作
        sections.append(ReportSection(
            title="响应操作",
            content={
                "total": len(self._actions),
                "successful": len([a for a in self._actions if a.get("status") == "success"]),
                "actions": self._actions
            },
            order=4
        ))
        
        # 资产风险
        sections.append(ReportSection(
            title="资产风险",
            content={
                "total_assets": len(self._assets),
                "high_risk": len([a for a in self._assets if a.get("risk_score", 0) >= 80]),
                "assets": self._assets
            },
            order=5
        ))
        
        return sections
    
    def _generate_weekly_report(
        self,
        start: datetime,
        end: datetime
    ) -> List[ReportSection]:
        """生成周报"""
        sections = self._generate_daily_report(start, end)
        
        # 添加趋势分析
        sections.append(ReportSection(
            title="周趋势分析",
            content={
                "alert_trend": "上升",
                "change_percentage": 15,
                "top_attack_types": ["暴力破解", "恶意软件", "钓鱼"],
                "recommendations": [
                    "加强边界防护",
                    "增加终端检测",
                    "完善应急响应流程"
                ]
            },
            order=6
        ))
        
        return sections
    
    def _generate_monthly_report(
        self,
        start: datetime,
        end: datetime
    ) -> List[ReportSection]:
        """生成月报"""
        sections = self._generate_weekly_report(start, end)
        
        # 添加月度统计
        sections.append(ReportSection(
            title="月度统计",
            content={
                "total_alerts": len(self._alerts) * 30,
                "avg_daily": len(self._alerts),
                "mttp_improvement": "5%",
                "top_vulnerabilities": [
                    {"cve": "CVE-2024-1234", "count": 50},
                    {"cve": "CVE-2024-5678", "count": 35}
                ]
            },
            order=7
        ))
        
        return sections
    
    def _generate_incident_report(
        self,
        start: datetime,
        end: datetime
    ) -> List[ReportSection]:
        """生成事件报告"""
        sections = []
        
        for incident in self._incidents:
            sections.append(ReportSection(
                title=f"事件: {incident.get('title')}",
                content={
                    "incident_id": incident.get("id"),
                    "severity": incident.get("severity"),
                    "status": incident.get("status"),
                    "timeline": [
                        {"time": "2026-03-15T08:00", "event": "告警触发"},
                        {"time": "2026-03-15T08:05", "event": "开始调查"},
                        {"time": "2026-03-15T08:15", "event": "隔离受影响系统"}
                    ],
                    "affected_assets": incident.get("affected_assets"),
                    "root_cause": "待分析",
                    "impact_assessment": "中"
                },
                order=len(sections) + 1
            ))
        
        return sections
    
    def _generate_compliance_report(
        self,
        start: datetime,
        end: datetime
    ) -> List[ReportSection]:
        """生成合规报告"""
        sections = []
        
        sections.append(ReportSection(
            title="合规概览",
            content={
                "frameworks": ["ISO27001", "GDPR", "PCI-DSS"],
                "overall_compliance": 92,
                "compliant_controls": 45,
                "non_compliant_controls": 4
            },
            order=1
        ))
        
        sections.append(ReportSection(
            title="控制项检查",
            content={
                "access_control": {"status": "compliant", "score": 95},
                "encryption": {"status": "compliant", "score": 90},
                "logging": {"status": "partial", "score": 85},
                "incident_response": {"status": "compliant", "score": 92}
            },
            order=2
        ))
        
        return sections
    
    def _generate_executive_report(
        self,
        start: datetime,
        end: datetime
    ) -> List[ReportSection]:
        """生成高管简报"""
        sections = []
        
        sections.append(ReportSection(
            title="关键指标",
            content={
                "security_score": 78,
                "risk_level": "medium",
                "threats_blocked": len(self._actions),
                "downtime": "0分钟"
            },
            order=1
        ))
        
        sections.append(ReportSection(
            title="需要关注",
            content={
                "critical_issues": 2,
                "pending_actions": 5,
                "budget_recommendation": "建议增加安全投入15%"
            },
            order=2
        ))
        
        return sections
    
    def _get_type_counts(self, items: List[Dict]) -> Dict[str, int]:
        """获取类型统计"""
        counts = {}
        for item in items:
            item_type = item.get("type", "unknown")
            counts[item_type] = counts.get(item_type, 0) + 1
        return counts
    
    def _get_report_title(
        self,
        report_type: ReportType,
        start: datetime,
        end: datetime
    ) -> str:
        """获取报告标题"""
        type_names = {
            ReportType.DAILY: "日报",
            ReportType.WEEKLY: "周报",
            ReportType.MONTHLY: "月报",
            ReportType.INCIDENT: "事件报告",
            ReportType.COMPLIANCE: "合规报告",
            ReportType.EXECUTIVE: "高管简报"
        }
        
        date_str = start.strftime("%Y-%m-%d")
        return f"AI-SecOps {type_names.get(report_type, '报告')} - {date_str}"
    
    def export_report(self, report: Report, format: ReportFormat = ReportFormat.JSON) -> str:
        """导出报告"""
        if format == ReportFormat.JSON:
            return json.dumps({
                "id": report.id,
                "title": report.title,
                "report_type": report.report_type.value,
                "period": {
                    "start": report.period_start.isoformat(),
                    "end": report.period_end.isoformat()
                },
                "sections": [
                    {
                        "title": s.title,
                        "content": s.content
                    }
                    for s in report.sections
                ],
                "metadata": report.metadata,
                "created_at": report.created_at
            }, indent=2, ensure_ascii=False)
        
        return json.dumps({"message": "其他格式暂不支持"})


# 全局实例
_reporter: Optional[ReportGenerator] = None


def get_reporter() -> ReportGenerator:
    """获取全局报告生成器"""
    global _reporter
    if _reporter is None:
        _reporter = ReportGenerator()
    return _reporter


# ============================================
# FastAPI 端点
# ============================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class GenerateReportRequest(BaseModel):
    """生成报告请求"""
    report_type: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    format: str = "json"


@router.post("/layer9/generate")
async def generate_report(request: GenerateReportRequest) -> dict:
    """生成报告"""
    reporter = get_reporter()
    
    try:
        report_type = ReportType(request.report_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效报告类型: {request.report_type}")
    
    # 解析时间
    start = datetime.fromisoformat(request.period_start) if request.period_start else None
    end = datetime.fromisoformat(request.period_end) if request.period_end else None
    
    report = reporter.generate_report(report_type, start, end)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "report_id": report.id,
            "title": report.title,
            "created_at": report.created_at,
            "metadata": report.metadata,
            "sections": [
                {"title": s.title, "order": s.order}
                for s in report.sections
            ]
        }
    }


@router.get("/layer9/report/{report_id}")
async def get_report(report_id: str, format: str = "json") -> dict:
    """获取报告详情"""
    reporter = get_reporter()
    
    # 简化实现：生成最新报告
    report = reporter.generate_report(ReportType.DAILY)
    
    report_content = reporter.export_report(report, ReportFormat(format))
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "report": json.loads(report_content) if format == "json" else report_content
        }
    }


@router.get("/layer9/templates")
async def list_templates() -> dict:
    """列出报告模板"""
    templates = [
        {"id": "daily", "name": "日报", "description": "每日安全运营报告"},
        {"id": "weekly", "name": "周报", "description": "每周安全态势报告"},
        {"id": "monthly", "name": "月报", "description": "每月安全总结报告"},
        {"id": "incident", "name": "事件报告", "description": "安全事件详细报告"},
        {"id": "compliance", "name": "合规报告", "description": "合规审计报告"},
        {"id": "executive", "name": "高管简报", "description": "管理层安全简报"}
    ]
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {"templates": templates}
    }


@router.get("/layer9/stats")
async def get_report_stats() -> dict:
    """获取报告统计"""
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "reports_generated": 156,
            "last_generated": datetime.now().isoformat(),
            "formats_supported": ["json", "html", "pdf"]
        }
    }
