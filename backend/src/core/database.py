"""
数据库配置与ORM模型
使用SQLAlchemy + Alembic
"""

import os
from typing import Optional
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Boolean, 
    Text, JSON, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool

# 数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_secops.db")

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=False
)

# 创建SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base
Base = declarative_base()


# ==================== 数据模型 ====================

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # admin, analyst, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    approvals = relationship("Approval", back_populates="user")


class Asset(Base):
    """资产表"""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # server, endpoint, database, firewall, iot, cloud
    ip_address = Column(String(50))
    mac_address = Column(String(50))
    status = Column(String(20), default="normal")  # normal, warning, critical, compromised
    risk_score = Column(Integer, default=0)
    owner = Column(String(100))
    department = Column(String(100))
    tags = Column(JSON, default={})
    properties = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    alerts = relationship("Alert", back_populates="asset")


class Alert(Base):
    """告警表"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, index=True, nullable=False)
    type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, info
    status = Column(String(20), default="new")  # new, investigating, mitigated, resolved
    
    source_ip = Column(String(50))
    target_ip = Column(String(50))
    description = Column(Text)
    
    asset_id = Column(Integer, ForeignKey("assets.id"))
    rule_id = Column(String(50))
    
    raw_log = Column(Text)
    enriched_data = Column(JSON, default={})
    
    assigned_to = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # 关系
    asset = relationship("Asset", back_populates="alerts")
    incidents = relationship("IncidentAlert", back_populates="alert")


class Incident(Base):
    """安全事件表"""
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(20), nullable=False)
    status = Column(String(20), default="open")  # open, investigating, contained, closed
    
    root_cause = Column(Text)
    impact_scope = Column(Text)
    affected_assets = Column(JSON, default=[])
    
    created_by = Column(String(50))
    assigned_to = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # 关系
    alerts = relationship("IncidentAlert", back_populates="incident")
    storyline = relationship("Storyline", back_populates="incident")


class IncidentAlert(Base):
    """事件-告警关联表"""
    __tablename__ = "incident_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    
    incident = relationship("Incident", back_populates="alerts")
    alert = relationship("Alert", back_populates="incidents")


class Storyline(Base):
    """攻击故事线表"""
    __tablename__ = "storylines"
    
    id = Column(Integer, primary_key=True, index=True)
    storyline_id = Column(String(50), unique=True, index=True, nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    
    title = Column(String(200))
    summary = Column(Text)
    mitre_tactics = Column(JSON, default=[])
    attack_chain = Column(JSON, default=[])
    
    confidence = Column(Integer, default=0)
    risk_score = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    incident = relationship("Incident", back_populates="storyline")


class Action(Base):
    """安全操作记录表"""
    __tablename__ = "actions"
    
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String(50), unique=True, index=True, nullable=False)
    
    action_type = Column(String(50), nullable=False)  # block_ip, quarantine, notify, etc.
    target = Column(JSON, nullable=False)
    parameters = Column(JSON, default={})
    
    status = Column(String(20), default="pending")  # pending, approved, executing, completed, failed
    result = Column(JSON, default={})
    
    playbook_id = Column(String(50))
    
    requested_by = Column(String(50))
    approved_by = Column(String(50))
    executed_by = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)


class Approval(Base):
    """HITL审批表"""
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    approval_id = Column(String(50), unique=True, index=True, nullable=False)
    
    action_id = Column(String(50), nullable=False)
    action_type = Column(String(50))
    target = Column(JSON)
    
    status = Column(String(20), default="pending")  # pending, approved, rejected
    reason = Column(Text)
    
    requester = Column(String(50))
    approver = Column(String(50))
    
    user_id = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # 关系
    user = relationship("User", back_populates="approvals")


class AuditLog(Base):
    """审计日志表"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(50), unique=True, index=True, nullable=False)
    
    user = Column(String(50))
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    details = Column(JSON, default={})
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 辅助函数 ====================

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表初始化完成")


# ==================== FastAPI依赖 ====================

from fastapi import Depends
from sqlalchemy.orm import Session

def get_database():
    """FastAPI数据库依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
