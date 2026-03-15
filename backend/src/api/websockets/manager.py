"""
WebSocket 管理器实现
支持实时推送：战时模式、HITL审批、告警推送
"""
import json
import uuid
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket
from loguru import logger


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃的WebSocket连接
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "global": set(),           # 全局告警
            "hitl": set(),            # HITL审批
            "assets": set(),          # 资产状态
            "storylines": set(),      # 故事线更新
            "war_mode": set(),        # 战时模式
        }
    
    async def connect(self, websocket: WebSocket, channel: str = "global"):
        """WebSocket连接"""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"WebSocket connected to channel: {channel}")
    
    def disconnect(self, websocket: WebSocket, channel: str = "global"):
        """WebSocket断开"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            logger.info(f"WebSocket disconnected from channel: {channel}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, message: dict, channel: str = "global"):
        """广播消息到指定频道"""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to channel {channel}: {e}")
                disconnected.add(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.active_connections[channel].discard(conn)
    
    # ==================== 业务推送方法 ====================
    
    async def push_asset_status_update(
        self,
        asset_id: str,
        new_status: str,
        trigger_war_mode: bool = False,
        glow_color: Optional[str] = None
    ):
        """推送资产状态更新"""
        message = {
            "type": "ASSET_STATUS_UPDATE",
            "trace_id": str(uuid.uuid4()),
            "payload": {
                "asset_id": asset_id,
                "new_status": new_status,
                "trigger_war_mode": trigger_war_mode,
                "glow_color": glow_color
            }
        }
        await self.broadcast(message, "assets")
        if trigger_war_mode:
            await self.broadcast(message, "war_mode")
    
    async def push_war_mode_triggered(self, threat_level: int):
        """推送战时模式触发"""
        message = {
            "type": "WAR_MODE_TRIGGERED",
            "trace_id": str(uuid.uuid4()),
            "payload": {
                "threat_level": threat_level,
                "timestamp": str(uuid.uuid4())
            }
        }
        await self.broadcast(message, "war_mode")
        await self.broadcast(message, "global")
    
    async def push_new_alert(self, alert: dict):
        """推送新告警"""
        message = {
            "type": "NEW_ALERT",
            "trace_id": alert.get("trace_id", str(uuid.uuid4())),
            "payload": alert
        }
        await self.broadcast(message, "global")
    
    async def push_hitl_approval_required(
        self,
        action: str,
        target_ip: str,
        risk_assessment: str,
        timeout: int = 300
    ):
        """推送HITL审批请求"""
        message = {
            "type": "HITL_APPROVAL_REQUIRED",
            "trace_id": str(uuid.uuid4()),
            "payload": {
                "action": action,
                "target_ip": target_ip,
                "risk_assessment": risk_assessment,
                "timeout": timeout
            }
        }
        await self.broadcast(message, "hitl")
    
    async def push_storyline_update(self, storyline: dict):
        """推送故事线更新"""
        message = {
            "type": "STORYLINE_UPDATE",
            "trace_id": storyline.get("trace_id", str(uuid.uuid4())),
            "payload": storyline
        }
        await self.broadcast(message, "storylines")


# 全局单例
websocket_manager = WebSocketManager()
