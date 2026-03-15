"""
Layer 4: 时序压缩层
时序数据聚合与降采样

功能：
- 时间窗口聚合
- 动态采样率调整
- 异常点保留
- 趋势分析
"""

import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum
from loguru import logger
from pydantic import BaseModel, Field


class AggregationType(str, Enum):
    """聚合类型"""
    SUM = "sum"
    AVG = "avg"
    MAX = "max"
    MIN = "min"
    COUNT = "count"
    DISTINCT = "distinct"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"


class TimeSeriesPoint(BaseModel):
    """时序数据点"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = Field(default_factory=dict)


class AggregatedMetric(BaseModel):
    """聚合指标"""
    metric_name: str
    time_window: str
    start_time: datetime
    end_time: datetime
    aggregation: AggregationType
    value: float
    sample_count: int
    tags: Dict[str, str] = Field(default_factory=dict)


class TimeSeriesCompressor:
    """时序数据压缩器"""
    
    def __init__(
        self,
        default_window: str = "5m",
        retention_periods: Dict[str, int] = None
    ):
        self.default_window = default_window
        self.retention_periods = retention_periods or {
            "1m": 24 * 3600,      # 1分钟粒度保留24小时
            "5m": 7 * 24 * 3600,   # 5分钟粒度保留7天
            "1h": 30 * 24 * 3600,  # 1小时粒度保留30天
            "1d": 365 * 24 * 3600  # 1天粒度保留1年
        }
        
        # 内存存储
        self._raw_data: Dict[str, List[TimeSeriesPoint]] = defaultdict(list)
        self._aggregated_data: Dict[str, Dict[str, List[AggregatedMetric]]] = defaultdict(
            lambda: defaultdict(list)
        )
        
        # 统计
        self.stats = {
            "total_points": 0,
            "compressed_points": 0,
            "compression_ratio": 0.0
        }
    
    def ingest(self, metric_name: str, points: List[TimeSeriesPoint]):
        """摄入时序数据"""
        self._raw_data[metric_name].extend(points)
        self.stats["total_points"] += len(points)
        
        # 自动触发聚合
        self._auto_aggregate(metric_name)
    
    def _auto_aggregate(self, metric_name: str):
        """自动聚合"""
        raw_points = self._raw_data.get(metric_name, [])
        if not raw_points:
            return
        
        # 按时间窗口聚合
        for window in ["1m", "5m", "1h", "1d"]:
            aggregated = self._aggregate_by_window(
                raw_points,
                window,
                AggregationType.AVG
            )
            self._aggregated_data[metric_name][window] = aggregated
        
        # 更新压缩比
        total_agg = sum(
            len(v) for v in self._aggregated_data[metric_name].values()
        )
        if total_agg > 0:
            self.stats["compressed_points"] = total_agg
            self.stats["compression_ratio"] = (
                self.stats["total_points"] / max(1, total_agg)
            )
    
    def _aggregate_by_window(
        self,
        points: List[TimeSeriesPoint],
        window: str,
        agg_type: AggregationType
    ) -> List[AggregatedMetric]:
        """按时间窗口聚合"""
        if not points:
            return []
        
        # 解析窗口大小
        window_seconds = self._parse_window(window)
        
        # 按窗口分组
        windows: Dict[int, List[TimeSeriesPoint]] = defaultdict(list)
        for point in points:
            window_key = int(point.timestamp.timestamp() / window_seconds)
            windows[window_key].append(point)
        
        # 聚合
        results = []
        for window_key, window_points in sorted(windows.items()):
            start_time = datetime.fromtimestamp(window_key * window_seconds)
            end_time = start_time + timedelta(seconds=window_seconds)
            
            values = [p.value for p in window_points]
            
            if agg_type == AggregationType.SUM:
                value = sum(values)
            elif agg_type == AggregationType.AVG:
                value = sum(values) / len(values) if values else 0
            elif agg_type == AggregationType.MAX:
                value = max(values) if values else 0
            elif agg_type == AggregationType.MIN:
                value = min(values) if values else 0
            elif agg_type == AggregationType.COUNT:
                value = len(values)
            else:
                value = sum(values) / len(values) if values else 0
            
            # 合并标签
            tags = {}
            for p in window_points:
                tags.update(p.tags)
            
            results.append(AggregatedMetric(
                metric_name=points[0].tags.get("metric", "unknown"),
                time_window=window,
                start_time=start_time,
                end_time=end_time,
                aggregation=agg_type,
                value=value,
                sample_count=len(window_points),
                tags=tags
            ))
        
        return results
    
    def _parse_window(self, window: str) -> int:
        """解析窗口大小（秒）"""
        if window.endswith("m"):
            return int(window[:-1]) * 60
        elif window.endswith("h"):
            return int(window[:-1]) * 3600
        elif window.endswith("d"):
            return int(window[:-1]) * 86400
        return 300  # 默认5分钟
    
    def query(
        self,
        metric_name: str,
        window: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        aggregation: AggregationType = AggregationType.AVG
    ) -> List[AggregatedMetric]:
        """查询聚合数据"""
        window = window or self.default_window
        
        if window in self._raw_data:
            # 实时聚合
            points = self._raw_data[metric_name]
            
            # 时间过滤
            if start_time or end_time:
                filtered = []
                for p in points:
                    if start_time and p.timestamp < start_time:
                        continue
                    if end_time and p.timestamp > end_time:
                        continue
                    filtered.append(p)
                points = filtered
            
            return self._aggregate_by_window(points, window, aggregation)
        
        return self._aggregated_data[metric_name].get(window, [])
    
    def get_trend(
        self,
        metric_name: str,
        window: str = "1h",
        hours: int = 24
    ) -> Dict[str, Any]:
        """获取趋势分析"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        data = self.query(metric_name, window, start_time, end_time)
        
        if not data:
            return {"trend": "unknown", "change_rate": 0}
        
        values = [m.value for m in data]
        
        # 计算趋势
        if len(values) >= 2:
            recent_avg = sum(values[-3:]) / min(3, len(values))
            older_avg = sum(values[:3]) / min(3, len(values))
            
            if older_avg > 0:
                change_rate = (recent_avg - older_avg) / older_avg
            else:
                change_rate = 0
            
            if change_rate > 0.2:
                trend = "increasing"
            elif change_rate < -0.2:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
            change_rate = 0
        
        return {
            "trend": trend,
            "change_rate": change_rate,
            "current_value": values[-1] if values else 0,
            "average_value": sum(values) / len(values) if values else 0,
            "min_value": min(values) if values else 0,
            "max_value": max(values) if values else 0,
            "data_points": len(values)
        }
    
    def detect_anomalies(
        self,
        metric_name: str,
        window: str = "5m",
        threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """异常检测"""
        data = self.query(metric_name, window)
        
        if len(data) < 10:
            return []
        
        values = [m.value for m in data]
        mean = sum(values) / len(values)
        
        # 计算标准差
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5
        
        anomalies = []
        for metric in data:
            if abs(metric.value - mean) > threshold * std_dev:
                anomalies.append({
                    "timestamp": metric.start_time.isoformat(),
                    "value": metric.value,
                    "expected_range": (mean - threshold * std_dev, mean + threshold * std_dev),
                    "deviation": abs(metric.value - mean) / max(std_dev, 0.01)
                })
        
        return anomalies
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "metrics_count": len(self._raw_data),
            "windows_available": list(self.retention_periods.keys())
        }


# 全局实例
_compressor: Optional[TimeSeriesCompressor] = None


def get_compressor() -> TimeSeriesCompressor:
    """获取全局压缩器"""
    global _compressor
    if _compressor is None:
        _compressor = TimeSeriesCompressor()
    return _compressor


# ============================================
# FastAPI 端点
# ============================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class IngestRequest(BaseModel):
    """数据摄入请求"""
    metric_name: str
    points: List[Dict[str, Any]]


class QueryRequest(BaseModel):
    """查询请求"""
    metric_name: str
    window: Optional[str] = "5m"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    aggregation: Optional[str] = "avg"


@router.post("/layer4/ingest")
async def ingest_data(request: IngestRequest) -> dict:
    """摄入时序数据"""
    compressor = get_compressor()
    
    points = []
    for p in request.points:
        point = TimeSeriesPoint(
            timestamp=datetime.fromisoformat(p.get("timestamp", datetime.now().isoformat())),
            value=float(p.get("value", 0)),
            tags=p.get("tags", {})
        )
        points.append(point)
    
    compressor.ingest(request.metric_name, points)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {"ingested": len(points)}
    }


@router.get("/layer4/query/{metric_name}")
async def query_data(
    metric_name: str,
    window: str = "5m",
    start_time: str = None,
    end_time: str = None,
    aggregation: str = "avg"
) -> dict:
    """查询聚合数据"""
    compressor = get_compressor()
    
    start = datetime.fromisoformat(start_time) if start_time else None
    end = datetime.fromisoformat(end_time) if end_time else None
    
    agg_type = AggregationType(aggregation)
    data = compressor.query(metric_name, window, start, end, agg_type)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "metrics": [
                {
                    "start_time": m.start_time.isoformat(),
                    "end_time": m.end_time.isoformat(),
                    "value": m.value,
                    "sample_count": m.sample_count
                }
                for m in data
            ],
            "total": len(data)
        }
    }


@router.get("/layer4/trend/{metric_name}")
async def get_trend(metric_name: str, window: str = "1h", hours: int = 24) -> dict:
    """获取趋势分析"""
    compressor = get_compressor()
    trend = compressor.get_trend(metric_name, window, hours)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": trend
    }


@router.get("/layer4/anomalies/{metric_name}")
async def detect_anomalies(
    metric_name: str,
    window: str = "5m",
    threshold: float = 2.0
) -> dict:
    """异常检测"""
    compressor = get_compressor()
    anomalies = compressor.detect_anomalies(metric_name, window, threshold)
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": {
            "anomalies": anomalies,
            "total": len(anomalies)
        }
    }


@router.get("/layer4/stats")
async def get_stats() -> dict:
    """获取统计"""
    compressor = get_compressor()
    
    return {
        "trace_id": str(uuid.uuid4()),
        "success": True,
        "data": compressor.get_stats()
    }
