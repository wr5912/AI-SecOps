/**
 * AISecOps - WebSocket Service Layer
 * Following FRONTEND_DESIGN_DOCUMENT.md Chapter 10.2
 *
 * Manages real-time connections for:
 * - Live alerts stream
 * - Asset status updates
 * - Storyline updates
 * - HITL approval notifications
 */

import { useAppStore, type Alert, type Asset, type Storyline, type ApprovalRequest } from '../stores/useAppStore';

// ==================== Event Types ====================

export type WebSocketEventType =
  | 'alert:new'
  | 'alert:update'
  | 'asset:status_change'
  | 'asset:new'
  | 'storyline:new'
  | 'storyline:update'
  | 'approval:request'
  | 'approval:update'
  | 'system:health'
  | 'threat:level_change';

export interface WebSocketMessage<T = unknown> {
  type: WebSocketEventType;
  payload: T;
  traceId?: string;
  timestamp: string;
}

// ==================== WebSocket Manager ====================

class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private listeners: Map<WebSocketEventType, Set<(payload: unknown) => void>> = new Map();
  private isConnecting = false;

  // Configuration
  private readonly baseUrl: string;

  constructor(baseUrl: string = import.meta.env.VITE_WS_URL || 'wss://api.AISecOps.local/ws') {
    this.baseUrl = baseUrl;
  }

  /**
   * Connect to WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      if (this.isConnecting) {
        reject(new Error('Already connecting...'));
        return;
      }

      this.isConnecting = true;

      try {
        this.ws = new WebSocket(this.baseUrl);

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          useAppStore.getState().setWsConnected(true);
          this.startHeartbeat();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('[WebSocket] Failed to parse message:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('[WebSocket] Disconnected');
          this.isConnecting = false;
          useAppStore.getState().setWsConnected(false);
          this.stopHeartbeat();
          this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
          this.isConnecting = false;
          reject(error);
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    useAppStore.getState().setWsConnected(false);
  }

  /**
   * Send message to server
   */
  send<T>(type: WebSocketEventType, payload: T, traceId?: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage<T> = {
        type,
        payload,
        traceId,
        timestamp: new Date().toISOString(),
      };
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] Cannot send message - not connected');
    }
  }

  /**
   * Subscribe to specific event type
   */
  subscribe<T>(type: WebSocketEventType, callback: (payload: T) => void): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)!.add(callback as (payload: unknown) => void);

    // Return unsubscribe function
    return () => {
      this.listeners.get(type)?.delete(callback as (payload: unknown) => void);
    };
  }

  /**
   * Handle incoming message and update store
   */
  private handleMessage(message: WebSocketMessage): void {
    const { type, payload, traceId } = message;

    // Update trace ID if present
    if (traceId) {
      useAppStore.getState().setCurrentTraceId(traceId);
    }

    // Notify listeners
    const typeListeners = this.listeners.get(type);
    if (typeListeners) {
      typeListeners.forEach((callback) => callback(payload));
    }

    // Update Zustand store based on message type
    switch (type) {
      case 'alert:new':
        this.handleNewAlert(payload as Alert);
        break;
      case 'alert:update':
        this.handleAlertUpdate(payload as Alert);
        break;
      case 'asset:status_change':
        this.handleAssetStatusChange(payload as { id: string; status: Asset['status'] });
        break;
      case 'storyline:new':
        this.handleNewStoryline(payload as Storyline);
        break;
      case 'storyline:update':
        this.handleStorylineUpdate(payload as Storyline);
        break;
      case 'approval:request':
        this.handleApprovalRequest(payload as ApprovalRequest);
        break;
      case 'threat:level_change':
        // Threat level is computed from assets, no action needed
        break;
      default:
        break;
    }
  }

  // ==================== Store Updates ====================

  private handleNewAlert(alert: Alert): void {
    useAppStore.getState().addAlert(alert);
    useAppStore.getState().addNotification({
      message: `新告警: ${alert.type}`,
      type: alert.level === 'critical' ? 'error' : alert.level === 'high' ? 'warning' : 'info',
    });
  }

  private handleAlertUpdate(alert: Alert): void {
    const { alerts } = useAppStore.getState();
    const index = alerts.findIndex((a) => a.id === alert.id);
    if (index !== -1) {
      const newAlerts = [...alerts];
      newAlerts[index] = alert;
      useAppStore.getState().setAlerts(newAlerts);
    }
  }

  private handleAssetStatusChange(data: { id: string; status: Asset['status'] }): void {
    useAppStore.getState().updateAsset(data.id, { status: data.status });

    if (data.status === 'compromised' || data.status === 'critical') {
      useAppStore.getState().addNotification({
        message: `资产状态变更: ${data.id} -> ${data.status}`,
        type: 'warning',
      });
    }
  }

  private handleNewStoryline(storyline: Storyline): void {
    const { storylines } = useAppStore.getState();
    useAppStore.getState().setStorylines([...storylines, storyline]);

    useAppStore.getState().addNotification({
      message: `新攻击故事线: ${storyline.title}`,
      type: storyline.severity === 'critical' ? 'error' : 'warning',
    });
  }

  private handleStorylineUpdate(storyline: Storyline): void {
    const { storylines } = useAppStore.getState();
    const index = storylines.findIndex((s) => s.id === storyline.id);
    if (index !== -1) {
      const newStorylines = [...storylines];
      newStorylines[index] = storyline;
      useAppStore.getState().setStorylines(newStorylines);
    }
  }

  private handleApprovalRequest(request: ApprovalRequest): void {
    useAppStore.getState().addApprovalRequest(request);
    useAppStore.getState().addNotification({
      message: `待审批请求: ${request.type} - ${request.target}`,
      type: 'warning',
    });
  }

  // ==================== Heartbeat ====================

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.send('system:health', { status: 'ping' });
    }, 30000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  // ==================== Reconnection ====================

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`[WebSocket] Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      setTimeout(() => this.connect().catch(() => {}), this.reconnectDelay);
    } else {
      console.error('[WebSocket] Max reconnection attempts reached');
      useAppStore.getState().addNotification({
        message: 'WebSocket连接失败，请刷新页面',
        type: 'error',
      });
    }
  }
}

// ==================== Singleton Instance ====================

export const wsManager = new WebSocketManager();

// ==================== React Hook ====================

/**
 * Custom hook for WebSocket connection with automatic cleanup
 */
export const useWebSocket = () => {
  const wsConnected = useAppStore((state) => state.wsConnected);

  return {
    connect: () => wsManager.connect(),
    disconnect: () => wsManager.disconnect(),
    send: wsManager.send.bind(wsManager),
    subscribe: wsManager.subscribe.bind(wsManager),
    isConnected: wsConnected,
  };
};

// ==================== Event Subscriptions ====================

/**
 * Setup default event subscriptions
 */
export const setupWebSocketListeners = () => {
  // Subscribe to new alerts
  wsManager.subscribe<Alert>('alert:new', (alert) => {
    console.log('[WebSocket] New alert:', alert.id);
  });

  // Subscribe to approval requests
  wsManager.subscribe<ApprovalRequest>('approval:request', (request) => {
    console.log('[WebSocket] Approval request:', request.id);
  });

  // Subscribe to asset status changes
  wsManager.subscribe<{ id: string; status: Asset['status'] }>('asset:status_change', (data) => {
    console.log('[WebSocket] Asset status change:', data.id, data.status);
  });
};

export default wsManager;
