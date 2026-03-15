"""
故事线数据模型
与前端TypeScript模型完全对齐
"""
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class StorylineSeverity(str, Enum):
    """故事线严重程度枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"


class StorylineStatus(str, Enum):
    """故事线状态枚举"""
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"


class StorylineStep(BaseModel):
    """故事线步骤"""
    time: str
    event: str
    node: str


class Storyline(BaseModel):
    """故事线模型 - 与前端完全对齐"""
    id: str
    trace_id: str
    title: str
    description: str
    severity: StorylineSeverity
    confidence_score: int
    assets: List[str]
    mitre_tactics: List[str] = []
    steps: List[StorylineStep]
    status: StorylineStatus
    aiReasoning: Optional[List[str]] = None


class StorylineListResponse(BaseModel):
    """故事线列表响应"""
    items: List[Storyline]
