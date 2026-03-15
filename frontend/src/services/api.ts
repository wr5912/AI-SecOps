/**
 * AISecOps - API Client
 * 前后端数据打通的API调用层
 */
import type { Asset, Alert, Storyline, ApprovalRequest } from '../stores/useAppStore'

// API基础URL - 可通过环境变量配置
const API_BASE_URL = 'http://localhost:8000'

// 通用请求方法
async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`)
  }
  
  const result = await response.json()
  
  // 统一处理响应格式
  if (result.trace_id) {
    return result.data
  }
  
  return result
}

// ==================== 资产 API ====================

export async function getAssets(params?: {
  page?: number
  page_size?: number
  status?: string
  asset_type?: string
}): Promise<{ items: Asset[]; total: number }> {
  const queryParams = new URLSearchParams()
  if (params?.page) queryParams.set('page', String(params.page))
  if (params?.page_size) queryParams.set('page_size', String(params.page_size))
  if (params?.status) queryParams.set('status', params.status)
  if (params?.asset_type) queryParams.set('asset_type', params.asset_type)
  
  const query = queryParams.toString()
  return request(`/api/v1/assets${query ? `?${query}` : ''}`)
}

export async function getAsset(assetId: string): Promise<Asset> {
  return request(`/api/v1/assets/${assetId}`)
}

export async function getAssetHologram(assetId: string): Promise<{
  asset: Asset
  related_assets: Asset[]
  recent_alerts: Alert[]
  network_connections: any[]
}> {
  return request(`/api/v1/assets/${assetId}/hologram`)
}

export async function executeAssetAction(
  assetId: string,
  action: string,
  parameters: Record<string, any> = {}
): Promise<{ status: string; result: string }> {
  return request(`/api/v1/assets/${assetId}/actions`, {
    method: 'POST',
    body: JSON.stringify({ action, parameters }),
  })
}

// ==================== 拓扑 API ====================

export async function getTopologyGraph(zoomLevel?: number): Promise<{
  nodes: any[]
  edges: any[]
}> {
  const query = zoomLevel ? `?zoom_level=${zoomLevel}` : ''
  return request(`/api/v1/topology/graph${query}`)
}

export async function getTopologyStats(): Promise<{
  total_assets: number
  by_type: Record<string, number>
  by_status: Record<string, number>
  average_risk_score: number
}> {
  return request('/api/v1/topology/stats')
}

// ==================== 告警 API ====================

export async function getIncidents(params?: {
  page?: number
  page_size?: number
  severity?: string
}): Promise<{ items: Alert[]; total: number }> {
  const queryParams = new URLSearchParams()
  if (params?.page) queryParams.set('page', String(params.page))
  if (params?.page_size) queryParams.set('page_size', String(params.page_size))
  if (params?.severity) queryParams.set('severity', params.severity)
  
  const query = queryParams.toString()
  return request(`/api/v1/incidents${query ? `?${query}` : ''}`)
}

export async function getIncident(traceId: string): Promise<{
  incident: Alert
  analysis: any
}> {
  return request(`/api/v1/incidents/${traceId}`)
}

export async function getStorylines(): Promise<{ items: Storyline[] }> {
  return request('/api/v1/storylines')
}

// ==================== 编排/HITL API ====================

export async function getPendingApprovals(): Promise<{
  items: ApprovalRequest[]
  total: number
}> {
  return request('/api/v1/orchestration/pending')
}

export async function approveTask(
  traceId: string,
  comment?: string
): Promise<{ message: string; status: string }> {
  return request(`/api/v1/orchestration/${traceId}/approve`, {
    method: 'POST',
    body: JSON.stringify({ comment }),
  })
}

export async function rejectTask(
  traceId: string,
  reason?: string
): Promise<{ message: string; status: string }> {
  return request(`/api/v1/orchestration/${traceId}/reject`, {
    method: 'POST',
    body: JSON.stringify({ reason }),
  })
}

// ==================== 反馈 API ====================

export async function submitFeedback(data: {
  trace_id: string
  target_type: string
  target_id: string
  feedback_type: string
  content?: string
  confidence_rating?: number
}): Promise<{ id: string; status: string }> {
  return request('/api/v1/feedback/submit', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getFeedbackList(traceId?: string): Promise<{ items: any[] }> {
  const query = traceId ? `?trace_id=${traceId}` : ''
  return request(`/api/v1/feedback${query}`)
}

// ==================== Copilot API ====================

export async function copilotChat(messages: {
  role: string
  content: string
}[], context?: Record<string, any>): Promise<{ message: { role: string; content: string } }> {
  return request('/api/v1/copilot/chat', {
    method: 'POST',
    body: JSON.stringify({ messages, context }),
  })
}

// SSE 流式响应处理
export function createCopilotStream(
  message: string,
  onMessage: (chunk: string) => void,
  onDone: () => void,
  onError: (error: Error) => void,
  context?: string
): EventSource {
  const params = new URLSearchParams({ message })
  if (context) params.set('context', context)
  
  const eventSource = new EventSource(`${API_BASE_URL}/api/v1/copilot/chat/stream?${params}`)
  
  eventSource.onmessage = (event) => {
    const data = event.data
    if (data === '[DONE]') {
      onDone()
      eventSource.close()
    } else {
      onMessage(data)
    }
  }
  
  eventSource.onerror = (error) => {
    onError(new Error('SSE connection error'))
    eventSource.close()
  }
  
  return eventSource
}

export default {
  getAssets,
  getAsset,
  getAssetHologram,
  executeAssetAction,
  getTopologyGraph,
  getTopologyStats,
  getIncidents,
  getIncident,
  getStorylines,
  getPendingApprovals,
  approveTask,
  rejectTask,
  submitFeedback,
  getFeedbackList,
  copilotChat,
  createCopilotStream,
}
