"""
Layer 1: 防洪网关层
基于Sigma规则的大规模告警过滤引擎

实现四级过滤架构：
- L0: 规则离线预编译
- L1: Aho-Corasick极速预过滤
- L2: SQLite内存数据库精确匹配
- L3: 序列关联与告警分发

参考文档: docs/基于Sigma规则的大规模告警过滤最佳实践指南.md
"""

import sqlite3
import orjson
import threading
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
from queue import Queue
from pydantic import BaseModel, Field
from loguru import logger

# 尝试导入Sigma库，如果不可用则使用简化实现
try:
    from sigma.collection import SigmaCollection
    from sigma.backends.sqlite import sqliteBackend
    from sigma.pipelines.sqlite import sqlite_pipeline
    SIGMA_AVAILABLE = True
except ImportError:
    SIGMA_AVAILABLE = False
    logger.warning("Sigma库不可用，使用简化过滤实现")

# 尝试导入pyahocorasick
try:
    import ahocorasick
    AHOCORASICK_AVAILABLE = True
except ImportError:
    AHOCORASICK_AVAILABLE = False
    logger.warning("pyahocorasick不可用，使用Python字符串匹配")


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logger


class AlertSeverity(str, Enum):
    """告警级别"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SigmaRule(BaseModel):
    """Sigma规则数据结构"""
    id: str
    title: str
    level: str
    logsource: Dict[str, Any] = {}
    sql_query: str = ""
    keywords: Set[str] = Field(default_factory=set)
    required_fields: Set[str] = Field(default_factory=set)
    mitre_tactics: List[str] = Field(default_factory=list)


class FilteredAlert(BaseModel):
    """过滤后的告警"""
    rule_id: str
    rule_title: str
    level: str
    log_data: Dict[str, Any] = {}
    timestamp: str
    trace_id: str
    mitre_tactics: List[str] = Field(default_factory=list)


class SigmaRuleLoader:
    """Sigma规则加载器"""
    
    def __init__(self, rules_dir: str):
        self.rules_dir = Path(rules_dir)
        self.rules: Dict[str, SigmaRule] = {}
        self.sql_queries: List[Tuple[str, str]] = []
    
    def load_rules(self) -> Dict[str, SigmaRule]:
        """加载并编译规则"""
        logger.info(f"[L0] 正在加载Sigma规则: {self.rules_dir}")
        
        # 查找规则文件
        rule_files = list(self.rules_dir.rglob("*.yml"))
        if not rule_files:
            logger.warning(f"未找到规则文件: {self.rules_dir}")
            return {}
        
        logger.info(f"发现 {len(rule_files)} 个规则文件")
        
        # 如果Sigma可用，使用Sigma库加载
        if SIGMA_AVAILABLE:
            try:
                rule_collection = SigmaCollection.from_yaml(
                    [str(p) for p in rule_files]
                )
                
                # 转换为SQL查询
                backend = sqliteBackend(sqlite_pipeline())
                self.sql_queries = backend.convert(rule_collection)
                
                # 构建规则对象
                for rule in rule_collection.rules:
                    rule_obj = SigmaRule(
                        id=rule.id,
                        title=rule.title,
                        level=str(rule.level) if rule.level else "medium",
                        logsource=dict(rule.logsource) if rule.logsource else {},
                        sql_query=""
                    )
                    
                    # 获取SQL查询
                    for sql_pair in self.sql_queries:
                        if sql_pair[0] == rule.id:
                            rule_obj.sql_query = sql_pair[1]
                            break
                    
                    # 提取特征词和字段
                    rule_obj.keywords = self._extract_keywords(rule)
                    rule_obj.required_fields = self._extract_fields(rule)
                    
                    self.rules[rule.id] = rule_obj
                    
            except Exception as e:
                logger.error(f"Sigma规则解析失败: {e}")
                # 回退到简化实现
                self._load_fallback_rules()
        else:
            self._load_fallback_rules()
        
        logger.info(f"[L0] 完成：{len(self.rules)} 条规则")
        return self.rules
    
    def _load_fallback_rules(self):
        """加载简化规则（当Sigma不可用时）"""
        # 添加一些示例规则
        fallback_rules = [
            {
                "id": "sigma-suspicious-powershell",
                "title": "可疑的PowerShell执行",
                "level": "high",
                "keywords": ["powershell", "-enc", "mimikatz", "invoke-"],
                "logsource": {"product": "windows", "service": "powershell"},
                "sql_query": "SELECT * FROM logs WHERE event = 'powershell'",
                "mitre_tactics": ["T1059"]
            },
            {
                "id": "sigma-suspicious-smb",
                "title": "可疑的SMB活动",
                "level": "high",
                "keywords": ["smb", "445", "lateral movement"],
                "logsource": {"product": "windows", "service": "security"},
                "sql_query": "SELECT * FROM logs WHERE event = 'smb'",
                "mitre_tactics": ["T1021"]
            },
            {
                "id": "sigma-brute-force",
                "title": "暴力破解尝试",
                "level": "critical",
                "keywords": ["failed logon", "invalid password", "brute force"],
                "logsource": {"product": "windows", "service": "security"},
                "sql_query": "SELECT * FROM logs WHERE event = 'logon'",
                "mitre_tactics": ["T1110"]
            },
            {
                "id": "sigma-sql-injection",
                "title": "SQL注入攻击",
                "level": "critical",
                "keywords": ["sql", "injection", "' or '1'='1", "union select"],
                "logsource": {"product": "waf"},
                "sql_query": "SELECT * FROM logs WHERE event = 'waf'",
                "mitre_tactics": ["T1190"]
            },
            {
                "id": "sigma-c2-communication",
                "title": "可疑的C2通信",
                "level": "critical",
                "keywords": ["c2", "command and control", "suspicious dns"],
                "logsource": {"product": "network"},
                "sql_query": "SELECT * FROM logs WHERE event = 'dns'",
                "mitre_tactics": ["T1071"]
            }
        ]
        
        for rule_data in fallback_rules:
            rule_obj = SigmaRule(
                id=rule_data["id"],
                title=rule_data["title"],
                level=rule_data["level"],
                logsource=rule_data.get("logsource", {}),
                sql_query=rule_data.get("sql_query", ""),
                keywords=set(rule_data.get("keywords", [])),
                required_fields=set(),
                mitre_tactics=rule_data.get("mitre_tactics", [])
            )
            self.rules[rule_obj.id] = rule_obj
    
    def _extract_keywords(self, rule) -> Set[str]:
        """从规则中提取特征词"""
        keywords = set()
        
        def traverse(obj):
            if hasattr(obj, 'detection_items'):
                for item in obj.detection_items:
                    if hasattr(item, 'value'):
                        value = item.value
                        if isinstance(value, str) and len(value) >= 3:
                            keywords.add(value.lower())
                        elif isinstance(value, list):
                            for v in value:
                                if isinstance(v, str) and len(v) >= 3:
                                    keywords.add(v.lower())
            if hasattr(obj, 'detections'):
                for det in obj.detections.values():
                    traverse(det)
        
        if hasattr(rule, 'detection'):
            traverse(rule.detection)
        
        return keywords
    
    def _extract_fields(self, rule) -> Set[str]:
        """从规则中提取所需字段"""
        fields = set()
        
        def traverse(obj):
            if hasattr(obj, 'detection_items'):
                for item in obj.detection_items:
                    if hasattr(item, 'key'):
                        fields.add(item.key)
            if hasattr(obj, 'detections'):
                for det in obj.detections.values():
                    traverse(det)
        
        if hasattr(rule, 'detection'):
            traverse(rule.detection)
        
        return fields


class AhoCorasickFilter:
    """Aho-Corasick极速预过滤器"""
    
    def __init__(self, keywords: Set[str]):
        self.keywords = keywords
        self.keyword_to_rules: Dict[str, Set[str]] = {}
        
        if AHOCORASICK_AVAILABLE and keywords:
            self._build_automaton()
        else:
            self.automaton = None
            logger.info("[L1] 使用简化字符串匹配")
    
    def _build_automaton(self):
        """构建Aho-Corasick自动机"""
        self.automaton = ahocorasick.Automaton()
        
        for keyword in self.keywords:
            if len(keyword) >= 3:  # 过滤短关键词
                self.automaton.add_word(keyword, keyword)
        
        self.automaton.make_automaton()
        logger.info(f"[L1] Aho-Corasick自动机构建完成: {len(self.keywords)} 个关键词")
    
    def match_keywords(self, text: str) -> Set[str]:
        """匹配文本中的关键词"""
        matched = set()
        
        if self.automaton:
            # 使用Aho-Corasick
            text_lower = text.lower()
            for end_idx, keyword in self.automaton.iter(text_lower):
                matched.add(keyword)
        else:
            # 使用简化字符串匹配
            text_lower = text.lower()
            for keyword in self.keywords:
                if keyword in text_lower:
                    matched.add(keyword)
        
        return matched


class SQLiteMatcher:
    """SQLite内存数据库精确匹配器"""
    
    def __init__(self):
        self.sqlite_settings = {
            "PRAGMA synchronous": "OFF",
            "PRAGMA journal_mode": "MEMORY",
            "PRAGMA temp_store": "MEMORY",
            "PRAGMA cache_size": "10000",
            "PRAGMA count_changes": "OFF",
            "PRAGMA auto_vacuum": "NONE"
        }
    
    def match(self, logs: List[Dict], rules: Dict[str, SigmaRule]) -> List[FilteredAlert]:
        """在SQLite中执行规则匹配"""
        if not logs or not rules:
            return []
        
        alerts = []
        
        # 连接内存数据库
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # 设置优化参数
        for pragma, value in self.sqlite_settings.items():
            try:
                cursor.execute(f"{pragma} = {value}")
            except:
                pass
        
        # 动态创建表
        all_keys = set()
        for log in logs:
            all_keys.update(log.keys())
        
        if not all_keys:
            return []
        
        columns = ['id INTEGER PRIMARY KEY', 'raw_json TEXT']
        for key in all_keys:
            safe_key = f'"{key}"' if key.replace('_', '').isalnum() else f'"{key.replace(" ", "_")}"'
            columns.append(f'{safe_key} TEXT')
        
        try:
            create_sql = f"CREATE TABLE logs ({', '.join(columns)})"
            cursor.execute(create_sql)
            
            # 插入数据
            for idx, log in enumerate(logs):
                values = [str(idx), orjson.dumps(log).decode('utf-8')]
                for key in all_keys:
                    values.append(str(log.get(key, '')))
                
                placeholders = ', '.join(['?'] * len(values))
                cursor.execute(f"INSERT INTO logs VALUES ({placeholders})", values)
            
            conn.commit()
            
            # 执行规则匹配
            for rule_id, rule in rules.items():
                # 简化匹配：检查关键词是否在原始JSON中
                for log in logs:
                    raw_text = orjson.dumps(log).decode('utf-8').lower()
                    matched_kw = set()
                    
                    for kw in rule.keywords:
                        if kw.lower() in raw_text:
                            matched_kw.add(kw)
                    
                    if matched_kw or not rule.keywords:
                        # 匹配成功
                        alert = FilteredAlert(
                            rule_id=rule_id,
                            rule_title=rule.title,
                            level=rule.level,
                            log_data=log,
                            timestamp=log.get('timestamp', log.get('time', time.strftime('%Y-%m-%dT%H:%M:%SZ'))),
                            trace_id=f"trk-{uuid.uuid4().hex[:12]}",
                            mitre_tactics=rule.mitre_tactics
                        )
                        alerts.append(alert)
        
        except Exception as e:
            logger.debug(f"SQLite匹配错误: {e}")
        finally:
            conn.close()
        
        return alerts


class FloodGateEngine:
    """防洪网关引擎
    
    实现四级过滤架构：
    - L0: 规则离线预编译
    - L1: Aho-Corasick极速预过滤
    - L2: SQLite内存数据库精确匹配
    - L3: 序列关联与告警分发
    """
    
    def __init__(
        self,
        rules_dir: str = "./configs/sigma_rules",
        batch_size: int = 5000,
        batch_timeout: float = 1.0
    ):
        self.rules_dir = rules_dir
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        
        # L0组件
        self.rule_loader = SigmaRuleLoader(rules_dir)
        self.rules: Dict[str, SigmaRule] = {}
        
        # L1组件
        self.filter: Optional[AhoCorasickFilter] = None
        self.keyword_to_rules: Dict[str, Set[str]] = {}
        
        # L2组件
        self.matcher = SQLiteMatcher()
        
        # L3组件
        self.alert_queue: Queue = Queue()
        
        # 统计
        self.stats = {
            "total_processed": 0,
            "total_matched": 0,
            "total_filtered": 0,
            "l1_filtered": 0,
            "l2_matched": 0
        }
        
        # 初始化
        self._initialize()
    
    def _initialize(self):
        """初始化引擎"""
        logger.info("🚀 防洪网关引擎初始化...")
        
        # L0: 加载规则
        self.rules = self.rule_loader.load_rules()
        
        # 构建L1索引
        all_keywords = set()
        for rule_id, rule in self.rules.items():
            for kw in rule.keywords:
                if kw not in self.keyword_to_rules:
                    self.keyword_to_rules[kw] = set()
                self.keyword_to_rules[kw].add(rule_id)
                all_keywords.add(kw)
        
        # 构建Aho-Corasick自动机
        self.filter = AhoCorasickFilter(all_keywords)
        
        logger.info(f"初始化完成: {len(self.rules)} 条规则")
    
    def process_log(self, raw_log: bytes) -> List[FilteredAlert]:
        """处理单条日志"""
        try:
            log_data = orjson.loads(raw_log)
        except orjson.JSONDecodeError:
            return []
        
        return self._process_single_log(log_data)
    
    def _process_single_log(self, log_data: Dict) -> List[FilteredAlert]:
        """处理单条解析后的日志"""
        self.stats["total_processed"] += 1
        
        # L1: 预过滤
        raw_text = orjson.dumps(log_data).decode('utf-8')
        matched_keywords = set()
        
        if self.filter:
            matched_keywords = self.filter.match_keywords(raw_text)
        
        if not matched_keywords and self.rules:
            # 没有匹配任何关键词，跳过
            self.stats["l1_filtered"] += 1
            self.stats["total_filtered"] += 1
            return []
        
        # L2: 精确匹配
        alerts = self.matcher.match([log_data], self.rules)
        
        if alerts:
            self.stats["l2_matched"] += len(alerts)
            self.stats["total_matched"] += len(alerts)
        
        return alerts
    
    def process_batch(self, raw_logs: List[bytes]) -> List[FilteredAlert]:
        """批次处理日志（推荐）"""
        all_alerts = []
        
        # 解析所有日志
        parsed_logs = []
        for raw_log in raw_logs:
            try:
                log_data = orjson.loads(raw_log)
                parsed_logs.append(log_data)
            except orjson.JSONDecodeError:
                continue
        
        if not parsed_logs:
            return []
        
        self.stats["total_processed"] += len(parsed_logs)
        
        # L1: 预过滤
        candidate_rule_ids = set()
        filtered_logs = []
        
        for log_data in parsed_logs:
            raw_text = orjson.dumps(log_data).decode('utf-8')
            matched_keywords = set()
            
            if self.filter:
                matched_keywords = self.filter.match_keywords(raw_text)
            
            if matched_keywords:
                # 记录可能匹配的规则
                for kw in matched_keywords:
                    if kw in self.keyword_to_rules:
                        candidate_rule_ids.update(self.keyword_to_rules[kw])
                filtered_logs.append(log_data)
        
        filtered_count = len(parsed_logs) - len(filtered_logs)
        self.stats["l1_filtered"] += filtered_count
        self.stats["total_filtered"] += filtered_count
        
        if not filtered_logs:
            return []
        
        # L2: 精确匹配
        # 只对候选规则进行匹配
        candidate_rules = {
            rid: self.rules[rid] 
            for rid in candidate_rule_ids 
            if rid in self.rules
        }
        
        alerts = self.matcher.match(filtered_logs, candidate_rules)
        
        if alerts:
            self.stats["l2_matched"] += len(alerts)
            self.stats["total_matched"] += len(alerts)
        
        return alerts
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        filter_rate = (
            self.stats["total_filtered"] / max(1, self.stats["total_processed"]) * 100
        )
        return {
            **self.stats,
            "filter_rate": f"{filter_rate:.1f}%"
        }


class FloodGateServer:
    """防洪网关服务封装"""
    
    def __init__(
        self,
        rules_dir: str = "./configs/sigma_rules",
        output_queue: Optional[Queue] = None,
        batch_size: int = 5000,
        batch_timeout: float = 1.0
    ):
        self.engine = FloodGateEngine(
            rules_dir=rules_dir,
            batch_size=batch_size,
            batch_timeout=batch_timeout
        )
        
        self.output_queue = output_queue or Queue()
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        
        self.log_buffer: List[bytes] = []
        self.buffer_lock = threading.Lock()
        self.last_flush_time = time.time()
        
        self.running = False
    
    def ingest(self, raw_log: bytes):
        """摄入单条日志"""
        with self.buffer_lock:
            self.log_buffer.append(raw_log)
            
            should_flush = (
                len(self.log_buffer) >= self.batch_size or
                time.time() - self.last_flush_time >= self.batch_timeout
            )
        
        if should_flush:
            self._flush_buffer()
    
    def _flush_buffer(self):
        """刷新缓冲区"""
        with self.buffer_lock:
            if not self.log_buffer:
                return
            
            batch = self.log_buffer.copy()
            self.log_buffer.clear()
            self.last_flush_time = time.time()
        
        # 处理批次
        alerts = self.engine.process_batch(batch)
        
        # 推送告警
        for alert in alerts:
            self.output_queue.put(alert)
        
        # 打印进度
        if self.engine.stats["total_processed"] % 100000 == 0:
            logger.info(f"防洪网关进度: {self.engine.get_stats()}")
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return self.engine.get_stats()


# 全局实例
_flood_gate_engine: Optional[FloodGateEngine] = None


def get_flood_gate_engine() -> FloodGateEngine:
    """获取全局防洪网关引擎"""
    global _flood_gate_engine
    if _flood_gate_engine is None:
        _flood_gate_engine = FloodGateEngine()
    return _flood_gate_engine


# ============================================
# FastAPI 端点
# ============================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class LogIngestRequest(BaseModel):
    """日志摄入请求"""
    logs: List[dict]
    source: str = "api"


@router.post("/layer1/ingest")
async def ingest_logs(request: LogIngestRequest) -> dict:
    """摄入日志"""
    engine = get_flood_gate_engine()
    
    # 转换为字节
    raw_logs = [orjson.dumps(log) for log in request.logs]
    
    # 处理
    alerts = engine.process_batch(raw_logs)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "processed": len(request.logs),
            "matched": len(alerts),
            "alerts": [
                {
                    "rule_id": a.rule_id,
                    "rule_title": a.rule_title,
                    "level": a.level,
                    "trace_id": a.trace_id,
                    "mitre_tactics": a.mitre_tactics
                }
                for a in alerts
            ]
        }
    }


@router.post("/layer1/ingest/raw")
async def ingest_raw_log(log: dict, source: str = "api") -> dict:
    """摄入单条原始日志"""
    engine = get_flood_gate_engine()
    
    raw_log = orjson.dumps(log)
    alerts = engine.process_log(raw_log)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "matched": len(alerts),
            "alerts": [
                {
                    "rule_id": a.rule_id,
                    "rule_title": a.rule_title,
                    "level": a.level,
                    "trace_id": a.trace_id
                }
                for a in alerts
            ]
        }
    }


@router.get("/layer1/stats")
async def get_flood_gate_stats() -> dict:
    """获取防洪网关统计"""
    engine = get_flood_gate_engine()
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": engine.get_stats()
    }


@router.get("/layer1/rules")
async def list_rules() -> dict:
    """列出所有规则"""
    engine = get_flood_gate_engine()
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "total": len(engine.rules),
            "rules": [
                {
                    "id": rule_id,
                    "title": rule.title,
                    "level": rule.level,
                    "keywords_count": len(rule.keywords)
                }
                for rule_id, rule in engine.rules.items()
            ]
        }
    }
