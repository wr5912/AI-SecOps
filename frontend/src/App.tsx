/**
 * AISecOps - Main Application
 * Optimized with Zustand state management and modular components
 */
import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Node,
  Edge,
  BackgroundVariant,
  NodeTypes,
  Handle,
  Position,
  MarkerType
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import {
  Shield, Activity, Server, AlertTriangle, Brain, Search, Menu, X,
  ChevronRight, Zap, Target, Lock, Terminal, MessageSquare, Plus,
  CheckCircle, Clock, AlertCircle, ArrowUpRight, ArrowDownRight,
  RefreshCw, Filter, Download, MoreVertical, Cpu, Wifi, Network,
  Bot, Command, Eye, Fingerprint, Bug, Skull, Radar, Globe,
  Box, Cpu as Chip, Smartphone, Cloud, Database, Wifi as WifiIcon,
  Lock as LockIcon, Unlock, ShieldCheck, ShieldAlert, Swords,
  Timer, TrendingUp, TrendingDown, CircleDot, Layers, Hexagon,
  Sparkles, Play, Pause, SkipForward, AlertOctagon, XCircle,
  CheckCheck, Users, FileText, Settings, Bell, HelpCircle,
  Check
} from 'lucide-react'

// Store & Services
import {
  useAppStore,
  selectPendingApprovalCount,
  selectUnacknowledgedAlerts,
  selectCriticalAssets,
  type Asset,
  type Alert,
  type Storyline,
  type ChatMessage,
  type ApprovalRequest
} from './stores/useAppStore'
import { useWebSocket, setupWebSocketListeners } from './services/websocket'

// Components
import { NotificationPanel, NotificationBadge } from './components/NotificationPanel'
import { AssetPanel, AssetPanelFloatingBadge } from './components/AssetPanel'
import { HITLApprovalPanel, HITLFloatingBadge } from './components/HITLApprovalPanel'
import { FeedbackPanel, InlineFeedback } from './components/FeedbackPanel'

// ==================== Mock Data ====================
// Updated to align with FRONTEND_DESIGN_DOCUMENT.md Chapter 4 Data Models

const mockAssets: Asset[] = [
  { id: 'fw-01', trace_id: 'trace-fw-01', name: '边界防火墙', ip: '10.0.0.1', type: 'firewall', status: 'normal', risk_score: 15, os: 'FortiOS 7.0', department: 'IT部', owner: '张工', ports: [443, 22], vulnerabilities: [], connections: ['srv-web-01', 'srv-db-01'], lastSeen: new Date().toISOString() },
  { id: 'srv-web-01', trace_id: 'trace-srv-web-01', name: 'Web服务器-ERP', ip: '10.0.0.25', type: 'server', status: 'critical', risk_score: 92, os: 'Ubuntu 22.04', department: 'IT部', owner: '李工', ports: [80, 443, 22, 3306], vulnerabilities: [{ cvss: 9.8, name: 'CVE-2024-0001' }, { cvss: 7.5, name: 'CVE-2023-44487' }], connections: ['fw-01', 'srv-db-01', 'srv-file-01'], lastSeen: new Date().toISOString() },
  { id: 'srv-db-01', trace_id: 'trace-srv-db-01', name: '核心数据库', ip: '10.0.0.30', type: 'database', status: 'warning', risk_score: 68, os: 'CentOS 8', department: '数据部', owner: '王工', ports: [5432, 22], vulnerabilities: [{ cvss: 6.5, name: 'CVE-2023-0002' }], connections: ['fw-01', 'srv-web-01'], lastSeen: new Date().toISOString() },
  { id: 'srv-file-01', trace_id: 'trace-srv-file-01', name: '文件服务器', ip: '10.0.0.40', type: 'server', status: 'normal', risk_score: 35, os: 'Windows Server 2022', department: 'IT部', owner: '赵工', ports: [445, 139], vulnerabilities: [], connections: ['srv-web-01'], lastSeen: new Date().toISOString() },
  { id: 'ep-finance-01', trace_id: 'trace-ep-finance-01', name: '财务工作站', ip: '10.0.1.88', type: 'endpoint', status: 'compromised', risk_score: 98, os: 'Windows 11', department: '财务部', owner: '陈财务', ports: [135, 445], vulnerabilities: [{ cvss: 9.8, name: 'CVE-2024-0003' }], connections: ['srv-web-01', 'srv-db-01'], lastSeen: new Date().toISOString() },
  { id: 'ep-hr-01', trace_id: 'trace-ep-hr-01', name: 'HR工作站', ip: '10.0.1.100', type: 'endpoint', status: 'normal', risk_score: 28, os: 'Windows 11', department: '人事部', owner: '刘HR', ports: [], vulnerabilities: [], connections: ['srv-web-01'], lastSeen: new Date().toISOString() },
  { id: 'iot-gateway', trace_id: 'trace-iot-gateway', name: 'IoT网关', ip: '10.0.2.10', type: 'iot', status: 'warning', risk_score: 72, os: 'Linux 5.4', department: '运维部', owner: '周运维', ports: [8080, 22], vulnerabilities: [{ cvss: 8.1, name: 'CVE-2023-0003' }], connections: ['fw-01'], lastSeen: new Date().toISOString() },
  { id: 'cloud-storage', trace_id: 'trace-cloud-storage', name: '云存储', ip: '172.16.0.50', type: 'cloud', status: 'normal', risk_score: 22, os: 'Linux', department: 'IT部', owner: '云团队', ports: [443], vulnerabilities: [], connections: ['srv-web-01'], lastSeen: new Date().toISOString() },
]

const mockAlerts: Alert[] = [
  { id: 'alert-001', trace_id: 'trace-alert-001', severity: 'critical', attacker_ip: '203.0.113.45', victim_ip: '10.0.0.25', type: 'SQL注入攻击', time: '14:32:15', mitre_tactic: 'T1190', confidence_score: 95, storyline_id: 'story-001', acknowledged: false },
  { id: 'alert-002', trace_id: 'trace-alert-002', severity: 'critical', attacker_ip: '10.0.1.88', victim_ip: '10.0.0.30', type: '异常横向移动-暴力破解', time: '14:30:42', mitre_tactic: 'T1210', confidence_score: 88, storyline_id: 'story-001', acknowledged: false },
  { id: 'alert-003', trace_id: 'trace-alert-003', severity: 'high', attacker_ip: '10.0.1.88', victim_ip: '10.0.0.40', type: '可疑文件传输', time: '14:28:33', mitre_tactic: 'T1041', confidence_score: 76, storyline_id: 'story-001', acknowledged: false },
  { id: 'alert-004', trace_id: 'trace-alert-004', severity: 'medium', attacker_ip: '10.0.1.88', victim_ip: '8.8.8.8', type: '可疑外联-C2通信', time: '14:25:18', mitre_tactic: 'T1071', confidence_score: 65, storyline_id: 'story-001', acknowledged: false },
  { id: 'alert-005', trace_id: 'trace-alert-005', severity: 'high', attacker_ip: '45.33.32.156', victim_ip: '10.0.0.1', type: '端口扫描', time: '14:20:00', mitre_tactic: 'T1595', confidence_score: 92, storyline_id: 'story-002', acknowledged: false },
]

const mockStorylines: Storyline[] = [
  {
    id: 'story-001',
    trace_id: 'trace-story-001',
    title: '财务主机被攻陷 - 横向移动攻击',
    description: '攻击者通过Web服务器漏洞进入系统，获取财务主机权限后尝试横向移动到核心数据库',
    severity: 'critical',
    confidence_score: 92,
    assets: ['srv-web-01', 'ep-finance-01', 'srv-db-01'],
    mitre_tactics: ['T1190', 'T1210', 'T1041', 'T1071'],
    steps: [
      { time: '14:15:00', event: '外部攻击-IP注入', node: 'srv-web-01' },
      { time: '14:20:00', event: '漏洞利用-获得shell', node: 'srv-web-01' },
      { time: '14:25:00', event: '内网探测-发现财务主机', node: 'srv-web-01' },
      { time: '14:28:00', event: '横向移动-攻陷财务主机', node: 'ep-finance-01' },
      { time: '14:30:00', event: '数据窃取-尝试连接数据库', node: 'ep-finance-01' },
    ],
    status: 'active',
    aiReasoning: ['检测到异常横向移动模式', '多个高危漏洞被利用', 'C2通信特征明显']
  }
]

// Mock approval requests for demo
const mockApprovals: ApprovalRequest[] = [
  {
    id: 'apr-001',
    type: 'isolation',
    target: '10.0.1.88 (财务工作站)',
    description: 'AI建议隔离受攻击主机以防止进一步横向移动',
    requester: 'Sec-Copilot AI',
    requestTime: '14:35:00',
    status: 'pending',
    traceId: 'trace-001',
    priority: 'critical'
  },
  {
    id: 'apr-002',
    type: 'block_ip',
    target: '203.0.113.45',
    description: '自动封禁检测到的恶意外部攻击源IP',
    requester: 'Sec-Copilot AI',
    requestTime: '14:34:30',
    status: 'pending',
    traceId: 'trace-002',
    priority: 'high'
  }
]

// ==================== Helper Functions ====================

const getStatusColor = (status: string, warMode: boolean) => {
  if (warMode) {
    return {
      normal: '#10B981',
      warning: '#F59E0B',
      critical: '#EF4444',
      compromised: '#DC2626'
    }[status] || '#6B7280'
  }
  return {
    normal: '#0EA5E9',
    warning: '#F59E0B',
    critical: '#EF4444',
    compromised: '#DC2626'
  }[status] || '#6B7280'
}

const getNodeIcon = (type: string) => {
  switch (type) {
    case 'server': return Server
    case 'endpoint': return Smartphone
    case 'database': return Database
    case 'firewall': return Shield
    case 'iot': return WifiIcon
    case 'cloud': return Cloud
    default: return Server
  }
}

// ==================== Custom Node Components ====================

const ServerNode = ({ data }: { data: any }) => {
  const { label, ip, status, warMode, isInStoryline, isSelected } = data
  const statusColor = getStatusColor(status, warMode)
  const Icon = getNodeIcon('server')

  return (
    <div className={`relative px-4 py-3 rounded-xl border-2 transition-all duration-300 min-w-[160px] ${
      isSelected
        ? warMode ? 'border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.6)]' : 'border-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.6)]'
        : warMode ? 'border-red-500/50' : 'border-slate-600'
    } ${warMode && isInStoryline ? 'bg-red-500/20' : 'bg-slate-900'}`}>
      <Handle type="target" position={Position.Left} className="!bg-slate-500 !w-3 !h-3" />

      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
          warMode && (status === 'critical' || status === 'compromised')
            ? 'bg-red-500/20'
            : 'bg-cyan-500/20'
        }`}>
          <Icon className="w-5 h-5" style={{ color: statusColor }} />
        </div>
        <div>
          <div className={`text-sm font-medium ${warMode && isInStoryline ? 'text-red-300' : 'text-white'}`}>
            {label}
          </div>
          <div className={`text-xs ${warMode ? 'text-red-400/60' : 'text-slate-500'}`}>
            {ip}
          </div>
        </div>
      </div>

      <div className={`absolute -top-1 -right-1 w-4 h-4 rounded-full border-2 border-slate-900 ${
        status === 'normal' ? 'bg-emerald-500' :
        status === 'warning' ? 'bg-amber-500' :
        'bg-red-500 animate-pulse'
      }`} />

      <Handle type="source" position={Position.Right} className="!bg-slate-500 !w-3 !h-3" />
    </div>
  )
}

const FirewallNode = ({ data }: { data: any }) => {
  const { label, ip, status, warMode, isInStoryline, isSelected } = data
  const statusColor = getStatusColor(status, warMode)

  return (
    <div className={`relative px-4 py-3 rounded-xl border-2 transition-all duration-300 min-w-[160px] ${
      isSelected
        ? warMode ? 'border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.6)]' : 'border-amber-400 shadow-[0_0_20px_rgba(251,191,36,0.6)]'
        : warMode ? 'border-red-500/50' : 'border-amber-500/50'
    } ${warMode && isInStoryline ? 'bg-red-500/20' : 'bg-slate-900'}`}>
      <Handle type="target" position={Position.Left} className="!bg-slate-500 !w-3 !h-3" />

      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
          warMode && status === 'critical' ? 'bg-red-500/20' : 'bg-amber-500/20'
        }`}>
          <Shield className="w-5 h-5" style={{ color: statusColor }} />
        </div>
        <div>
          <div className={`text-sm font-medium ${warMode && isInStoryline ? 'text-red-300' : 'text-white'}`}>
            {label}
          </div>
          <div className={`text-xs ${warMode ? 'text-red-400/60' : 'text-slate-500'}`}>
            {ip}
          </div>
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-slate-500 !w-3 !h-3" />
    </div>
  )
}

const DatabaseNode = ({ data }: { data: any }) => {
  const { label, ip, status, warMode, isInStoryline, isSelected } = data
  const statusColor = getStatusColor(status, warMode)

  return (
    <div className={`relative px-4 py-3 rounded-xl border-2 transition-all duration-300 min-w-[160px] ${
      isSelected
        ? warMode ? 'border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.6)]' : 'border-purple-400 shadow-[0_0_20px_rgba(192,132,252,0.6)]'
        : warMode ? 'border-red-500/50' : 'border-purple-500/50'
    } ${warMode && isInStoryline ? 'bg-red-500/20' : 'bg-slate-900'}`}>
      <Handle type="target" position={Position.Left} className="!bg-slate-500 !w-3 !h-3" />

      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
          warMode && status === 'warning' ? 'bg-red-500/20' : 'bg-purple-500/20'
        }`}>
          <Database className="w-5 h-5" style={{ color: statusColor }} />
        </div>
        <div>
          <div className={`text-sm font-medium ${warMode && isInStoryline ? 'text-red-300' : 'text-white'}`}>
            {label}
          </div>
          <div className={`text-xs ${warMode ? 'text-red-400/60' : 'text-slate-500'}`}>
            {ip}
          </div>
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-slate-500 !w-3 !h-3" />
    </div>
  )
}

const EndpointNode = ({ data }: { data: any }) => {
  const { label, ip, status, warMode, isInStoryline, isSelected } = data
  const statusColor = getStatusColor(status, warMode)

  return (
    <div className={`relative px-4 py-3 rounded-full border-2 transition-all duration-300 min-w-[140px] ${
      isSelected
        ? warMode ? 'border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.6)]' : 'border-emerald-400 shadow-[0_0_20px_rgba(52,211,153,0.6)]'
        : warMode ? 'border-red-500/50' : 'border-emerald-500/50'
    } ${warMode && isInStoryline ? 'bg-red-500/20' : 'bg-slate-900'}`}>
      <Handle type="target" position={Position.Left} className="!bg-slate-500 !w-3 !h-3" />

      <div className="flex items-center gap-2">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          warMode && (status === 'critical' || status === 'compromised')
            ? 'bg-red-500/20'
            : 'bg-emerald-500/20'
        }`}>
          <Smartphone className="w-4 h-4" style={{ color: statusColor }} />
        </div>
        <div>
          <div className={`text-xs font-medium ${warMode && isInStoryline ? 'text-red-300' : 'text-white'}`}>
            {label}
          </div>
          <div className={`text-[10px] ${warMode ? 'text-red-400/60' : 'text-slate-500'}`}>
            {ip}
          </div>
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-slate-500 !w-3 !h-3" />
    </div>
  )
}

const IoTNode = ({ data }: { data: any }) => {
  const { label, ip, status, warMode, isInStoryline, isSelected } = data
  const statusColor = getStatusColor(status, warMode)

  return (
    <div className={`relative px-4 py-3 rounded-lg border-2 transition-all duration-300 min-w-[140px] ${
      isSelected
        ? warMode ? 'border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.6)]' : 'border-orange-400 shadow-[0_0_20px_rgba(251,146,60,0.6)]'
        : warMode ? 'border-red-500/50' : 'border-orange-500/50'
    } ${warMode && isInStoryline ? 'bg-red-500/20' : 'bg-slate-900'}`}>
      <Handle type="target" position={Position.Left} className="!bg-slate-500 !w-3 !h-3" />

      <div className="flex items-center gap-2">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
          warMode && status === 'warning' ? 'bg-red-500/20' : 'bg-orange-500/20'
        }`}>
          <WifiIcon className="w-4 h-4" style={{ color: statusColor }} />
        </div>
        <div>
          <div className={`text-xs font-medium ${warMode && isInStoryline ? 'text-red-300' : 'text-white'}`}>
            {label}
          </div>
          <div className={`text-[10px] ${warMode ? 'text-red-400/60' : 'text-slate-500'}`}>
            {ip}
          </div>
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-slate-500 !w-3 !h-3" />
    </div>
  )
}

const CloudNode = ({ data }: { data: any }) => {
  const { label, ip, status, warMode, isInStoryline, isSelected } = data
  const statusColor = getStatusColor(status, warMode)

  return (
    <div className={`relative px-4 py-3 rounded-xl border-2 transition-all duration-300 min-w-[140px] ${
      isSelected
        ? warMode ? 'border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.6)]' : 'border-blue-400 shadow-[0_0_20px_rgba(96,165,250,0.6)]'
        : warMode ? 'border-red-500/50' : 'border-blue-500/50'
    } ${warMode && isInStoryline ? 'bg-red-500/20' : 'bg-slate-900'}`}>
      <Handle type="target" position={Position.Left} className="!bg-slate-500 !w-3 !h-3" />

      <div className="flex items-center gap-2">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center bg-blue-500/20`}>
          <Cloud className="w-4 h-4" style={{ color: statusColor }} />
        </div>
        <div>
          <div className={`text-xs font-medium ${warMode && isInStoryline ? 'text-red-300' : 'text-white'}`}>
            {label}
          </div>
          <div className={`text-[10px] ${warMode ? 'text-red-400/60' : 'text-slate-500'}`}>
            {ip}
          </div>
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-slate-500 !w-3 !h-3" />
    </div>
  )
}

const nodeTypes: NodeTypes = {
  server: ServerNode,
  firewall: FirewallNode,
  database: DatabaseNode,
  endpoint: EndpointNode,
  iot: IoTNode,
  cloud: CloudNode,
}

// ==================== Network Canvas ====================

const NetworkCanvas = () => {
  const {
    assets,
    setAssets,
    selectedAssetId,
    selectAsset,
    warMode,
    storylines,
    selectedStorylineId
  } = useAppStore()

  const assetList = useMemo(() => Object.values(assets), [assets])
  const currentStoryline = useMemo(
    () => storylines.find(s => s.id === selectedStorylineId) || null,
    [storylines, selectedStorylineId]
  )

  // Initialize assets on mount
  useEffect(() => {
    setAssets(mockAssets)
  }, [setAssets])

  // Compute nodes based on assetList
  const computedNodes: Node[] = useMemo(() => {
    if (assetList.length === 0) return []

    const centerX = 400
    const centerY = 300
    const radius = 250

    return assetList.map((asset, index) => {
      const angle = (index / assetList.length) * 2 * Math.PI - Math.PI / 2
      const x = centerX + radius * Math.cos(angle)
      const y = centerY + radius * Math.sin(angle)

      return {
        id: asset.id,
        type: asset.type,
        position: { x, y },
        data: {
          label: asset.name,
          ip: asset.ip,
          status: asset.status,
          warMode,
          isInStoryline: currentStoryline?.assets.includes(asset.id),
          isSelected: selectedAssetId === asset.id
        }
      }
    })
  }, [assetList, warMode, currentStoryline, selectedAssetId])

  // Compute edges based on assetList
  const computedEdges: Edge[] = useMemo(() => {
    const edges: Edge[] = []

    assetList.forEach(asset => {
      asset.connections.forEach(connId => {
        // Only add edge if target exists in assetList
        if (assetList.find(a => a.id === connId)) {
          const isAttackPath = currentStoryline?.assets.includes(asset.id) &&
            currentStoryline?.assets.includes(connId)

          edges.push({
            id: `${asset.id}-${connId}`,
            source: asset.id,
            target: connId,
            type: 'smoothstep',
            animated: warMode && isAttackPath,
            style: {
              stroke: warMode && isAttackPath ? '#EF4444' : warMode ? '#7F1D1D' : '#475569',
              strokeWidth: warMode && isAttackPath ? 3 : 2
            },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: warMode && isAttackPath ? '#EF4444' : '#475569'
            }
          })
        }
      })
    })

    return edges
  }, [assetList, warMode, currentStoryline])

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])

  // Sync nodes when computedNodes changes
  useEffect(() => {
    if (computedNodes.length > 0) {
      setNodes(computedNodes)
    }
  }, [computedNodes, setNodes])

  // Sync edges when computedEdges changes
  useEffect(() => {
    if (computedEdges.length > 0) {
      setEdges(computedEdges)
    }
  }, [computedEdges, setEdges])

  useEffect(() => {
    setNodes(nodes => nodes.map(node => ({
      ...node,
      data: {
        ...node.data,
        isSelected: selectedAssetId === node.id,
        isInStoryline: currentStoryline?.assets.includes(node.id),
        warMode
      }
    })))
  }, [selectedAssetId, currentStoryline, warMode, setNodes])

  useEffect(() => {
    setEdges(edges => edges.map(edge => {
      const isAttackPath = currentStoryline?.assets.includes(edge.source) &&
        currentStoryline?.assets.includes(edge.target)

      return {
        ...edge,
        animated: warMode && !!isAttackPath,
        style: {
          stroke: warMode && isAttackPath ? '#EF4444' : warMode ? '#7F1D1D' : '#475569',
          strokeWidth: warMode && isAttackPath ? 3 : 2
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: warMode && isAttackPath ? '#EF4444' : '#475569'
        }
      }
    }))
  }, [warMode, currentStoryline, setEdges])

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      selectAsset(node.id === selectedAssetId ? null : node.id)
    },
    [selectAsset, selectedAssetId]
  )

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.5}
        maxZoom={2}
        defaultEdgeOptions={{ type: 'smoothstep' }}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={30}
          size={1}
          color={warMode ? '#450A0A' : '#1E293B'}
        />
        <Controls
          className={`!rounded-lg !shadow-xl ${
            warMode 
              ? '!bg-red-900/80 !border-red-500/50' 
              : '!bg-slate-800/90 !border-slate-700'
          }`}
          showZoom
          showFitView
          showInteractive={false}
        />
        <MiniMap
          nodeColor={(node) => {
            const status = node.data?.status
            if (warMode) {
              return status === 'critical' || status === 'compromised' ? '#EF4444' : '#7F1D1D'
            }
            return status === 'critical' || status === 'compromised' ? '#EF4444' : '#0EA5E9'
          }}
          maskColor={warMode ? 'rgba(127, 29, 29, 0.8)' : 'rgba(15, 23, 42, 0.8)'}
          className={`!rounded-lg ${warMode ? '!border-red-500/50' : '!border-slate-700'}`}
          style={{ 
            backgroundColor: warMode ? '#1a0a0a' : '#0f172a',
            ...(warMode ? { border: '1px solid rgba(239, 68, 68, 0.3)' } : {})
          }}
        />
      </ReactFlow>
    </div>
  )
}

// ==================== AI Copilot ====================

const AICopilot = () => {
  const {
    copilotOpen,
    toggleCopilot,
    selectedAssetId,
    copilotMessages,
    addCopilotMessage,
    selectAsset,
    addApprovalRequest
  } = useAppStore()

  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const quickActions = [
    '分析当前告警',
    '查询恶意IP情报',
    '建议响应措施',
    '生成事件报告',
    '查找受影响资产'
  ]

  // Initialize with welcome message
  useEffect(() => {
    if (copilotMessages.length === 0) {
      addCopilotMessage({
        id: `welcome-${Date.now()}`,
        trace_id: 'trace-welcome',
        role: 'assistant',
        content: '您好！我是安全AI助手。可以帮我：\n\n• 分析安全事件和攻击链路\n• 查询威胁情报 (IOC)\n• 建议响应处置方案\n• 解释告警和漏洞\n\n也可以直接点击画布上的资产，我会提供上下文分析。',
        timestamp: new Date()
      })
    }
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [copilotMessages])

  const handleSend = () => {
    if (!input.trim()) return

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      trace_id: `trace-msg-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date()
    }
    addCopilotMessage(userMsg)
    setInput('')
    setIsLoading(true)

    setTimeout(() => {
      let responseContent = ''
      let actions: ChatMessage['actions'] = []

      if (input.includes('分析') || input.includes('攻击')) {
        responseContent = `根据当前态势分析：

**威胁等级**: 🔴 高级 (Score: 92/100)

**攻击链摘要**:
1. 攻击源IP: 203.0.113.45 (已识别为恶意扫描节点)
2. 初始入口: Web服务器 (CVE-2024-0001)
3. 横向移动: 财务工作站已被攻陷
4. 目标: 核心数据库 (尝试爆破中)

**MITRE ATT&CK 映射**:
- T1190: 应用层漏洞利用
- T1210: 远程服务利用
- T1041: 协议外泄

**建议立即执行**:
1. 隔离财务主机网络
2. 封禁攻击源IP
3. 启动数据库审计日志`
        actions = [
          { label: '📍 隔离主机', action: 'isolate' },
          { label: '🚫 封禁IP', action: 'block_ip' }
        ]
      } else if (input.includes('查询') || input.includes('情报')) {
        responseContent = `威胁情报查询结果:

**IP: 203.0.113.45**
- 来源: AbuseIPDB
- 可信度: 92%
- 标签: 僵尸网络, 暴力破解, 扫描
- 历史攻击: 15,234 次
- 最后活跃: 30分钟前
- 地理: 美国 加利福尼亚州

**建议动作**: 添加到防火墙黑名单`
        actions = [
          { label: '➕ 添加黑名单', action: 'add_blacklist' }
        ]
      } else {
        responseContent = `我理解您的请求。

当前系统状态:
- 活跃告警: 5 条 (2条严重)
- 受影响资产: 3 台
- 建议优先处理: 财务主机被攻陷事件

请告诉我您想了解的具体内容，或点击画布上的资产获取详细分析。`
      }

      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        trace_id: `trace-msg-${Date.now()}`,
        role: 'assistant',
        content: responseContent,
        timestamp: new Date(),
        actions
      }
      addCopilotMessage(aiMsg)
      setIsLoading(false)
    }, 1500)
  }

  const handleAction = (action: string) => {
    // Create HITL approval request
    if (action === 'isolate') {
      addApprovalRequest({
        id: `apr-${Date.now()}`,
        type: 'isolation',
        target: '10.0.1.88 (财务工作站)',
        description: 'AI建议隔离受攻击主机以防止进一步横向移动',
        requester: 'Sec-Copilot AI',
        requestTime: new Date().toLocaleTimeString('zh-CN'),
        status: 'pending',
        traceId: `trace-${Date.now()}`,
        priority: 'critical'
      })
    } else if (action === 'block_ip') {
      addApprovalRequest({
        id: `apr-${Date.now()}`,
        type: 'block_ip',
        target: '203.0.113.45',
        description: 'AI建议封禁恶意攻击源IP',
        requester: 'Sec-Copilot AI',
        requestTime: new Date().toLocaleTimeString('zh-CN'),
        status: 'pending',
        traceId: `trace-${Date.now()}`,
        priority: 'high'
      })
    }
  }

  if (!copilotOpen) {
    return (
      <button
        onClick={toggleCopilot}
        className="fixed right-4 bottom-4 w-14 h-14 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 text-white shadow-lg flex items-center justify-center hover:scale-110 transition-transform z-50"
      >
        <Bot className="w-6 h-6" />
      </button>
    )
  }

  return (
    <div className="fixed right-0 top-0 bottom-0 w-[400px] glass border-l border-slate-700/50 flex flex-col z-50 backdrop-blur-xl bg-slate-900/90">
      <div className="p-4 border-b border-slate-700/50 flex items-center justify-between bg-gradient-to-r from-cyan-500/10 to-purple-500/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-semibold text-white flex items-center gap-2">
              Sec-Copilot
              <span className="px-1.5 py-0.5 text-[10px] bg-cyan-500/20 text-cyan-400 rounded">AI</span>
            </div>
            <div className="text-xs text-slate-400">安全智能助手</div>
          </div>
        </div>
        <button onClick={toggleCopilot} className="p-2 rounded-lg hover:bg-slate-700/50 text-slate-400">
          <X className="w-5 h-5" />
        </button>
      </div>

      {selectedAssetId && (
        <div className="p-3 mx-4 mt-4 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
          <div className="flex items-center gap-2 text-cyan-400 text-sm mb-2">
            <Fingerprint className="w-4 h-4" />
            已选中资产上下文
          </div>
          <div className="text-xs text-slate-300">
            资产ID: {selectedAssetId} | 风险等级: <span className="text-red-400">高危</span>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {copilotMessages.map(msg => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[90%] rounded-2xl p-4 ${
              msg.role === 'user'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white'
                : 'bg-slate-800/80 border border-slate-700/50 text-slate-200'
            }`}>
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>

              {msg.actions && msg.actions.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-slate-600/30">
                  {msg.actions.map((action, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleAction(action.action)}
                      className="px-3 py-1.5 text-xs bg-slate-700/50 hover:bg-cyan-500/20 hover:text-cyan-400 rounded-lg transition-colors"
                    >
                      {action.label}
                    </button>
                  ))}
                  <div className="w-full pt-2 mt-2 border-t border-slate-600/20">
                    <div className="text-[10px] text-slate-500 mb-1">对该建议的评价:</div>
                    <InlineFeedback targetId={msg.id} targetType="DISPOSAL_RECOMMENDATION" />
                  </div>
                </div>
              )}

              <div className="text-[10px] text-slate-500 mt-2">
                {msg.timestamp.toLocaleTimeString('zh-CN')}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-800/80 border border-slate-700/50 rounded-2xl p-4">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="px-4 pb-2 flex gap-2 flex-wrap">
        {quickActions.map((action, idx) => (
          <button
            key={idx}
            onClick={() => setInput(action)}
            className="px-2 py-1 text-xs bg-slate-800/50 hover:bg-slate-700 text-slate-400 hover:text-cyan-400 rounded-md transition-colors"
          >
            {action}
          </button>
        ))}
      </div>

      <div className="p-4 border-t border-slate-700/50">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="输入您的问题..."
            className="flex-1 px-4 py-3 bg-slate-800/80 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
          <button
            onClick={handleSend}
            disabled={isLoading}
            className="px-4 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-xl hover:opacity-90 disabled:opacity-50"
          >
            <MessageSquare className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}

// ==================== Storyline Panel ====================

// Common panel dimensions
const PANEL_WIDTH = 'w-80' // 320px
const PANEL_GAP = 4 // gap-4 = 16px

const StorylinePanel = () => {
  const {
    storylines,
    setStorylines,
    selectedStorylineId,
    selectStoryline,
    warMode
  } = useAppStore()

  // Initialize storylines
  useEffect(() => {
    if (storylines.length === 0) {
      setStorylines(mockStorylines)
    }
  }, [storylines.length, setStorylines])

  // Calculate max height: 45% of viewport height minus HUD and gaps
  // Viewport height = 100vh, HUD = 56px, gaps = 32px, so max = (100vh - 56px - 32px) * 0.45
  return (
    <div className={`absolute left-20 transition-all duration-500 ${PANEL_WIDTH}`}
      style={{ 
        top: '56px', // Below HUD (h-14 = 56px)
        maxHeight: 'calc((100vh - 88px) * 0.45)', // 45% max, with gap consideration
        height: 'auto' // Auto height, scroll if exceeds max
      }}
    >
      <div className="h-full flex flex-col gap-4 overflow-y-auto">
        {storylines.map(storyline => (
          <div
            key={storyline.id}
            onClick={() => selectStoryline(selectedStorylineId === storyline.id ? null : storyline.id)}
            className={`flex-shrink-0 rounded-xl border transition-all duration-300 cursor-pointer backdrop-blur ${
              selectedStorylineId === storyline.id
                ? warMode
                  ? 'bg-red-500/20 border-red-500/50 shadow-[0_0_30px_rgba(239,68,68,0.3)]'
                  : 'bg-cyan-500/20 border-cyan-500/50 shadow-[0_0_30px_rgba(6,182,212,0.3)]'
                : 'bg-slate-900/80 border-slate-700/50 hover:border-slate-600'
            }`}
            style={{ height: 'auto' }}
          >
            <div className="p-4 border-b border-slate-700/30">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 text-xs rounded ${
                    storyline.severity === 'critical'
                      ? warMode ? 'bg-red-500/30 text-red-400' : 'bg-red-500/20 text-red-400'
                      : warMode ? 'bg-orange-500/30 text-orange-400' : 'bg-orange-500/20 text-orange-400'
                  }`}>
                    {storyline.severity === 'critical' ? '严重' : '高危'}
                  </span>
                  <span className="text-xs text-slate-500">{storyline.id}</span>
                </div>
                <InlineFeedback targetId={storyline.id} targetType="STORYLINE" />
              </div>
              <h4 className={`text-sm font-semibold ${warMode ? 'text-red-300' : 'text-white'}`}>
                {storyline.title}
              </h4>
            </div>

            <div className="p-4 overflow-y-auto" style={{ maxHeight: 'calc(100% - 80px)' }}>
              <p className="text-xs text-slate-400 mb-3 line-clamp-2">{storyline.description}</p>

              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${warMode ? 'bg-red-500' : 'bg-cyan-500'}`}
                      style={{ width: `${storyline.confidence_score}%` }}
                    />
                  </div>
                  <span className={`text-xs font-medium ${warMode ? 'text-red-400' : 'text-cyan-400'}`}>
                    {storyline.confidence_score}%
                  </span>
                </div>
                <span className="text-xs text-slate-500">{storyline.mitre_tactics.length} 个战术</span>
              </div>

              <div className="space-y-2">
                {storyline.steps.slice(-3).map((step, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs">
                    <div className={`w-1.5 h-1.5 rounded-full ${warMode ? 'bg-red-500' : 'bg-cyan-500'}`} />
                    <span className="text-slate-500">{step.time}</span>
                    <span className="text-slate-300 truncate">{step.event}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ==================== Asset Hologram Card ====================

const AssetHologramCard = () => {
  const { selectedAssetId, selectAsset, assets, addApprovalRequest, addNotification, warMode } = useAppStore()

  const asset = selectedAssetId ? assets[selectedAssetId] : null

  if (!asset) return null

  const handleAction = (action: string) => {
    if (action === 'isolate') {
      addApprovalRequest({
        id: `apr-${Date.now()}`,
        type: 'isolation',
        target: `${asset.ip} (${asset.name})`,
        description: '用户手动请求隔离资产',
        requester: 'Analyst',
        requestTime: new Date().toLocaleTimeString('zh-CN'),
        status: 'pending',
        traceId: `trace-${Date.now()}`,
        priority: 'high'
      })
    } else if (action === 'block_ip') {
      addApprovalRequest({
        id: `apr-${Date.now()}`,
        type: 'block_ip',
        target: asset.ip,
        description: '用户手动请求封禁IP',
        requester: 'Analyst',
        requestTime: new Date().toLocaleTimeString('zh-CN'),
        status: 'pending',
        traceId: `trace-${Date.now()}`,
        priority: 'high'
      })
    }
  }

  // Calculate position: below StorylinePanel (45% + gap) and 45% height
  // StorylinePanel: top 56px, height calc(45% - 32px)
  // Gap: 16px
  // AssetHologramCard: top = 56px + 45% + 16px = below StorylinePanel
  return (
    <div 
      className={`absolute left-20 backdrop-blur-xl bg-slate-900/95 border border-slate-700/50 rounded-2xl shadow-2xl z-40 overflow-hidden transition-all duration-500 ${PANEL_WIDTH}`}
      style={{ 
        top: 'calc(45% + 24px)', // Below StorylinePanel (45% + gap)
        maxHeight: 'calc((100vh - 88px) * 0.45)', // 45% max, with gap consideration
        height: 'auto', // Auto height, scroll if exceeds max
        overflowY: 'auto'
      }}
    >
      <div className={`p-4 border-b border-slate-700/30 sticky top-0 ${
        warMode
          ? 'bg-gradient-to-r from-red-500/20 to-orange-500/20'
          : 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
              warMode ? 'bg-red-500/20' : 'bg-cyan-500/20'
            }`}>
              <Server className={`w-6 h-6 ${warMode ? 'text-red-400' : 'text-cyan-400'}`} />
            </div>
            <div>
              <h3 className="font-semibold text-white">{asset.name}</h3>
              <p className="text-xs text-slate-400">{asset.type.toUpperCase()}</p>
            </div>
          </div>
          <button onClick={() => selectAsset(null)} className="p-1.5 rounded-lg hover:bg-slate-700/50 text-slate-400">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="p-4 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <div className="text-xs text-slate-500 mb-1">IP 地址</div>
            <div className="text-sm font-mono text-cyan-400">{asset.ip}</div>
          </div>
          <div>
            <div className="text-xs text-slate-500 mb-1">风险评分</div>
            <div className={`text-sm font-bold ${
              asset.risk_score > 80 ? 'text-red-400' : asset.risk_score > 60 ? 'text-orange-400' : 'text-emerald-400'
            }`}>{asset.risk_score}/100</div>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-slate-800/50">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs text-slate-500">资产所有者</div>
              <div className="text-sm text-white">{asset.owner}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-slate-500">所属部门</div>
              <div className="text-sm text-slate-300">{asset.department}</div>
            </div>
          </div>
        </div>

        {asset.vulnerabilities.length > 0 && (
          <div>
            <div className="text-xs text-slate-500 mb-2">高危漏洞 ({asset.vulnerabilities.length})</div>
            <div className="space-y-2">
              {asset.vulnerabilities.map((vuln, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 rounded bg-red-500/10 border border-red-500/20">
                  <span className="text-xs text-red-400">{vuln.name}</span>
                  <span className={`text-xs font-bold ${
                    vuln.cvss >= 9 ? 'text-red-400' : 'text-orange-400'
                  }`}>{vuln.cvss}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div>
          <div className="text-xs text-slate-500 mb-2">开放端口</div>
          <div className="flex flex-wrap gap-1">
            {asset.ports.map((port, idx) => (
              <span key={idx} className="px-2 py-1 text-xs bg-slate-800 text-slate-300 rounded">
                {port}
              </span>
            ))}
          </div>
        </div>

        <div className="pt-3 border-t border-slate-700/30">
          <div className="text-xs text-slate-500 mb-2">快速响应</div>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => {
                handleAction('isolate')
                selectAsset(null)
              }}
              className="px-3 py-2 text-xs bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-all flex items-center justify-center gap-1 active:scale-95 cursor-pointer"
            >
              <LockIcon className="w-3.5 h-3.5" />
              隔离主机
            </button>
            <button
              onClick={() => {
                handleAction('block_ip')
                selectAsset(null)
              }}
              className="px-3 py-2 text-xs bg-orange-500/20 hover:bg-orange-500/30 text-orange-400 rounded-lg transition-all flex items-center justify-center gap-1 active:scale-95 cursor-pointer"
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              封禁IP
            </button>
            <button
              onClick={() => {
                addNotification({
                  message: '漏洞扫描任务已提交',
                  type: 'info'
                })
              }}
              className="px-3 py-2 text-xs bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-lg transition-all flex items-center justify-center gap-1 active:scale-95 cursor-pointer"
            >
              <Bug className="w-3.5 h-3.5" />
              漏洞扫描
            </button>
            <button
              onClick={() => {
                addNotification({
                  message: '深度分析任务已提交',
                  type: 'info'
                })
              }}
              className="px-3 py-2 text-xs bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-lg transition-all flex items-center justify-center gap-1 active:scale-95 cursor-pointer"
            >
              <Search className="w-3.5 h-3.5" />
              深度分析
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ==================== Navigation Sidebar ====================

type NavigationView = 'threats' | 'approvals' | 'alerts' | 'assets' | 'reports'

interface SidebarProps {
  currentView: NavigationView;
  onViewChange: (view: NavigationView) => void;
  warMode: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ currentView, onViewChange, warMode }) => {
  const navItems = [
    { id: 'threats' as NavigationView, label: '威胁处置', icon: Shield, badge: 3 },
    { id: 'approvals' as NavigationView, label: '审批管理', icon: CheckCheck, badge: 2 },
    { id: 'alerts' as NavigationView, label: '告警管理', icon: AlertTriangle, badge: 5 },
    { id: 'assets' as NavigationView, label: '资产管理', icon: Server, badge: 8 },
    { id: 'reports' as NavigationView, label: '报告管理', icon: FileText, badge: 0 },
  ]

  return (
    <div className={`fixed left-0 top-0 bottom-0 w-20 flex flex-col items-center py-6 z-40 transition-all duration-500 ${
      warMode ? 'bg-red-900/30 border-r border-red-500/30' : 'bg-slate-900/80 border-r border-slate-700/50'
    }`}>
      {/* Logo */}
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-8 ${
        warMode ? 'bg-red-500/20' : 'bg-cyan-500/20'
      }`}>
        <Shield className={`w-7 h-7 ${warMode ? 'text-red-400' : 'text-cyan-400'}`} />
      </div>

      {/* Navigation Items */}
      <div className="flex flex-col gap-4 flex-1">
        {navItems.map(item => {
          const Icon = item.icon
          const isActive = currentView === item.id
          
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`relative w-14 h-14 rounded-xl flex flex-col items-center justify-center transition-all duration-300 ${
                isActive
                  ? warMode
                    ? 'bg-red-500/30 text-red-300 shadow-[0_0_20px_rgba(239,68,68,0.4)]'
                    : 'bg-cyan-500/20 text-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.3)]'
                  : warMode
                    ? 'text-red-400/60 hover:bg-red-500/10 hover:text-red-300'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5 mb-1" />
              <span className="text-[10px]">{item.label}</span>
              {item.badge > 0 && (
                <span className={`absolute -top-1 -right-1 w-5 h-5 text-[10px] font-bold rounded-full flex items-center justify-center ${
                  warMode ? 'bg-red-500 text-white' : 'bg-red-500 text-white'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Settings & User */}
      <div className="flex flex-col gap-4 mt-auto">
        <button className={`w-14 h-14 rounded-xl flex items-center justify-center transition-all ${
          warMode ? 'text-red-400/60 hover:bg-red-500/10' : 'text-slate-400 hover:bg-slate-800/50'
        }`}>
          <Settings className="w-5 h-5" />
        </button>
        <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white text-sm font-medium ${
          warMode ? 'bg-red-500/30' : 'bg-gradient-to-br from-cyan-500 to-purple-500'
        }`}>
          S
        </div>
      </div>
    </div>
  )
}

// ==================== HUD ====================

interface HUDProps {
  onNotificationClick?: () => void;
}

const HUD: React.FC<HUDProps> = ({ onNotificationClick }) => {
  const { warMode, toggleWarMode, alerts, assets, addNotification, pendingApprovals, setAlerts } = useAppStore()
  const [currentTime, setCurrentTime] = useState(new Date())

  // Initialize alerts
  useEffect(() => {
    if (alerts.length === 0) {
      setAlerts(mockAlerts)
    }
  }, [alerts.length, setAlerts])

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const assetList = Object.values(assets)
  const alertCount = alerts.filter(a => !a.acknowledged).length
  const pendingApprovalCount = pendingApprovals.filter(a => a.status === 'pending').length
  const totalNotificationCount = alertCount + pendingApprovalCount
  const assetCount = assetList.length
  const onlinePercent = Math.round((assetList.filter(a => a.status !== 'compromised').length / assetCount) * 100) || 0
  const threatLevel = warMode ? 92 : Math.min(100, Math.round((alerts.filter(a => a.severity === 'critical').length / 5) * 100) + 30)

  return (
    <div className={`fixed top-0 left-20 right-0 h-14 backdrop-blur-xl border-b z-30 transition-all duration-500 ${
      warMode
        ? 'bg-red-900/20 border-red-500/30 shadow-[0_0_30px_rgba(239,68,68,0.2)]'
        : 'bg-slate-900/80 border-slate-700/50'
    }`}>
      <div className="h-full px-4 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
              warMode ? 'bg-red-500/20' : 'bg-cyan-500/20'
            }`}>
              <Shield className={`w-6 h-6 ${warMode ? 'text-red-400' : 'text-cyan-400'}`} />
            </div>
            <div>
              <div className="font-bold text-white">AISecOps</div>
              <div className="text-[10px] text-slate-400">智能安全运营平台</div>
            </div>
          </div>

          <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-slate-800/50">
            <Radar className={`w-4 h-4 ${warMode ? 'text-red-400 animate-pulse' : 'text-cyan-400'}`} />
            <span className="text-xs text-slate-400">威胁指数</span>
            <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-1000 ${
                  warMode ? 'bg-red-500' : threatLevel > 70 ? 'bg-red-500' : threatLevel > 40 ? 'bg-orange-500' : 'bg-emerald-500'
                }`}
                style={{ width: `${threatLevel}%` }}
              />
            </div>
            <span className={`text-sm font-bold ${
              warMode ? 'text-red-400' : threatLevel > 70 ? 'text-red-400' : threatLevel > 40 ? 'text-orange-400' : 'text-emerald-400'
            }`}>{threatLevel}</span>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <button
            onClick={toggleWarMode}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-500 ${
              warMode
                ? 'bg-red-500/20 text-red-400 border border-red-500/30 shadow-[0_0_20px_rgba(239,68,68,0.3)]'
                : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
            }`}
          >
            {warMode ? <Swords className="w-4 h-4 animate-pulse" /> : <ShieldCheck className="w-4 h-4" />}
            <span className="text-sm font-medium">{warMode ? '⚔️ 战时模式' : '🛡️ 平时模式'}</span>
          </button>

          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5 px-3 py-2">
              <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
              <span className="text-slate-400">告警</span>
              <span className="text-white font-medium">{alertCount}</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-2">
              <Server className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-slate-400">资产</span>
              <span className="text-white font-medium">{assetCount}</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-2">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-slate-400">在线</span>
              <span className="text-white font-medium">{onlinePercent}%</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="搜索资产、告警..."
              className="w-64 pl-10 pr-12 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-300 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-0.5 text-[10px] text-slate-500">
              <kbd className="px-1 py-0.5 bg-slate-700 rounded">⌘</kbd>
              <kbd className="px-1 py-0.5 bg-slate-700 rounded">K</kbd>
            </div>
          </div>

          <div className="text-right font-mono">
            <div className="text-sm text-white">{currentTime.toLocaleTimeString('zh-CN')}</div>
            <div className="text-[10px] text-slate-500">{currentTime.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', weekday: 'short' })}</div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onNotificationClick}
              className="relative p-2 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-white"
            >
              <Bell className="w-5 h-5" />
              {totalNotificationCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center animate-pulse">
                  {totalNotificationCount}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      {warMode && (
        <div className="absolute top-full left-0 right-0 h-1 bg-gradient-to-r from-red-500 via-orange-500 to-red-500 animate-pulse" />
      )}
    </div>
  )
}

// ==================== Toast Notification ====================

const ToastNotification = () => {
  const { notifications, removeNotification } = useAppStore()

  useEffect(() => {
    notifications.forEach(notif => {
      const timer = setTimeout(() => {
        removeNotification(notif.id)
      }, 5000)
      return () => clearTimeout(timer)
    })
  }, [notifications, removeNotification])

  return (
    <>
      {notifications.slice(0, 3).map(notif => (
        <div
          key={notif.id}
          className="fixed top-20 right-4 px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-pulse"
        >
          <CheckCheck className="w-4 h-4 text-emerald-400" />
          <span className="text-sm text-white">{notif.message}</span>
        </div>
      ))}
    </>
  )
}

// ==================== Main App ====================

function App() {
  const { toggleWarMode, addApprovalRequest, setAlerts, setStorylines, alerts, storylines, selectAsset } = useAppStore()

  const [hitlPanelOpen, setHitlPanelOpen] = useState(false)
  const [feedbackPanelOpen, setFeedbackPanelOpen] = useState(false)
  const [notificationPanelOpen, setNotificationPanelOpen] = useState(false)
  const [assetPanelOpen, setAssetPanelOpen] = useState(false)
  const [currentView, setCurrentView] = useState<NavigationView>('threats')

  const alertCount = alerts.filter(a => !a.acknowledged).length
  const pendingApprovalCount = useAppStore(state => 
    state.pendingApprovals.filter(a => a.status === 'pending').length
  )
  const totalNotificationCount = alertCount + pendingApprovalCount

  // Initialize mock data in store
  useEffect(() => {
    if (alerts.length === 0) setAlerts(mockAlerts)
    if (storylines.length === 0) setStorylines(mockStorylines)
    // Add mock approval requests
    mockApprovals.forEach(apr => addApprovalRequest(apr))
  }, [])

  // Connect to WebSocket (optional - would work with real backend)
  const { isConnected } = useWebSocket()

  const warMode = useAppStore(state => state.warMode)

  const handleExecuteAction = useCallback((action: string) => {
    useAppStore.getState().addNotification({
      message: `${action} 执行成功`,
      type: 'success',
    })
  }, [])

  return (
    <div className={`h-screen overflow-hidden transition-all duration-500 ${
      warMode ? 'bg-red-950' : 'bg-slate-950'
    }`}>
      {/* Background Effects */}
      <div className={`fixed inset-0 pointer-events-none transition-opacity duration-1000 ${
        warMode ? 'opacity-100' : 'opacity-30'
      }`}>
        <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 via-transparent to-orange-500/5" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-red-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl animate-pulse" />
      </div>

      <Sidebar 
        currentView={currentView} 
        onViewChange={setCurrentView} 
        warMode={warMode} 
      />

      <HUD 
        onNotificationClick={() => setNotificationPanelOpen(true)}
      />

      <div className={`pt-14 pl-20 h-full ${currentView !== 'threats' ? 'hidden' : ''}`}>
        <NetworkCanvas />
      </div>

      <AssetHologramCard />
      <StorylinePanel />
      <AICopilot />

      <NotificationBadge onClick={() => setNotificationPanelOpen(true)} />

      <HITLApprovalPanel
        isOpen={hitlPanelOpen}
        onClose={() => setHitlPanelOpen(false)}
      />

      <FeedbackPanel
        isOpen={feedbackPanelOpen}
        onClose={() => setFeedbackPanelOpen(false)}
      />

      <NotificationPanel
        isOpen={notificationPanelOpen}
        onClose={() => setNotificationPanelOpen(false)}
      />

      <AssetPanel
        isOpen={assetPanelOpen}
        onClose={() => setAssetPanelOpen(false)}
      />

      <ToastNotification />
    </div>
  )
}

export default App
