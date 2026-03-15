import { useState, useMemo } from 'react'
import { X, Search, Filter, Server, Smartphone, Database, Shield, Wifi, Cloud, AlertTriangle, ShieldAlert, Lock, Unlock, Eye, Download, RefreshCw, MoreVertical, ChevronRight } from 'lucide-react'
import { useAppStore, type Asset } from '../stores/useAppStore'

interface AssetPanelProps {
  isOpen: boolean
  onClose: () => void
}

export const AssetPanel: React.FC<AssetPanelProps> = ({ isOpen, onClose }) => {
  const { assets, selectAsset, warMode } = useAppStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'name' | 'risk' | 'ip'>('name')

  const assetList = useMemo(() => {
    let result = Object.values(assets)

    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(a => 
        a.name.toLowerCase().includes(term) ||
        a.ip.includes(term) ||
        a.owner.includes(term) ||
        a.department.includes(term)
      )
    }

    // Type filter
    if (filterType !== 'all') {
      result = result.filter(a => a.type === filterType)
    }

    // Status filter
    if (filterStatus !== 'all') {
      result = result.filter(a => a.status === filterStatus)
    }

    // Sort
    result.sort((a, b) => {
      if (sortBy === 'name') return a.name.localeCompare(b.name)
      if (sortBy === 'risk') return b.risk_score - a.risk_score
      return a.ip.localeCompare(b.ip)
    })

    return result
  }, [assets, searchTerm, filterType, filterStatus, sortBy])

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'server': return Server
      case 'endpoint': return Smartphone
      case 'database': return Database
      case 'firewall': return Shield
      case 'iot': return Wifi
      case 'cloud': return Cloud
      default: return Server
    }
  }

  const getStatusColor = (status: string) => {
    if (warMode) {
      return {
        normal: 'bg-emerald-500',
        warning: 'bg-amber-500',
        critical: 'bg-red-500',
        compromised: 'bg-red-600 animate-pulse'
      }[status] || 'bg-slate-500'
    }
    return {
      normal: 'bg-cyan-500',
      warning: 'bg-amber-500',
      critical: 'bg-red-500',
      compromised: 'bg-red-600 animate-pulse'
    }[status] || 'bg-slate-500'
  }

  const getRiskColor = (score: number) => {
    if (warMode) {
      return score > 80 ? 'text-red-400' : score > 60 ? 'text-orange-400' : 'text-emerald-400'
    }
    return score > 80 ? 'text-red-400' : score > 60 ? 'text-orange-400' : 'text-cyan-400'
  }

  const typeOptions = [
    { value: 'all', label: '全部类型' },
    { value: 'server', label: '服务器' },
    { value: 'endpoint', label: '终端' },
    { value: 'database', label: '数据库' },
    { value: 'firewall', label: '防火墙' },
    { value: 'iot', label: 'IoT设备' },
    { value: 'cloud', label: '云资源' },
  ]

  const statusOptions = [
    { value: 'all', label: '全部状态' },
    { value: 'normal', label: '正常' },
    { value: 'warning', label: '警告' },
    { value: 'critical', label: '严重' },
    { value: 'compromised', label: '已攻陷' },
  ]

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      
      <div className={`relative w-full max-w-6xl h-[80vh] rounded-2xl border flex flex-col ${
        warMode 
          ? 'bg-red-950/95 border-red-500/30' 
          : 'bg-slate-900/95 border-slate-700/50'
      }`}>
        {/* Header */}
        <div className={`p-4 border-b flex items-center justify-between ${
          warMode ? 'border-red-500/30' : 'border-slate-700/50'
        }`}>
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
              warMode ? 'bg-red-500/20' : 'bg-cyan-500/20'
            }`}>
              <Server className={`w-5 h-5 ${warMode ? 'text-red-400' : 'text-cyan-400'}`} />
            </div>
            <div>
              <h2 className={`text-lg font-semibold ${warMode ? 'text-red-300' : 'text-white'}`}>
                资产管理
              </h2>
              <p className={`text-xs ${warMode ? 'text-red-400/60' : 'text-slate-500'}`}>
                共 {assetList.length} 项资产
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className={`p-2 rounded-lg hover:bg-slate-700/50 ${warMode ? 'text-red-400' : 'text-slate-400'}`}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filters */}
        <div className={`p-4 border-b ${warMode ? 'border-red-500/30' : 'border-slate-700/50'}`}>
          <div className="flex flex-wrap gap-4 items-center">
            {/* Search */}
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="搜索资产名称、IP、负责人..."
                className={`w-full pl-10 pr-4 py-2 rounded-lg border text-sm ${
                  warMode 
                    ? 'bg-slate-800/80 border-red-500/30 text-white placeholder-red-400/50 focus:border-red-400' 
                    : 'bg-slate-800/50 border-slate-700 text-white placeholder-slate-500 focus:border-cyan-500'
                }`}
              />
            </div>

            {/* Type Filter */}
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className={`px-3 py-2 rounded-lg border text-sm ${
                warMode 
                  ? 'bg-slate-800/80 border-red-500/30 text-red-300' 
                  : 'bg-slate-800/50 border-slate-700 text-slate-300'
              }`}
            >
              {typeOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>

            {/* Status Filter */}
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className={`px-3 py-2 rounded-lg border text-sm ${
                warMode 
                  ? 'bg-slate-800/80 border-red-500/30 text-red-300' 
                  : 'bg-slate-800/50 border-slate-700 text-slate-300'
              }`}
            >
              {statusOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className={`px-3 py-2 rounded-lg border text-sm ${
                warMode 
                  ? 'bg-slate-800/80 border-red-500/30 text-red-300' 
                  : 'bg-slate-800/50 border-slate-700 text-slate-300'
              }`}
            >
              <option value="name">按名称排序</option>
              <option value="risk">按风险排序</option>
              <option value="ip">按IP排序</option>
            </select>
          </div>
        </div>

        {/* Asset List */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {assetList.map(asset => {
              const Icon = getTypeIcon(asset.type)
              const statusColor = getStatusColor(asset.status)
              
              return (
                <div
                  key={asset.id}
                  onClick={() => {
                    selectAsset(asset.id)
                    onClose()
                  }}
                  className={`p-4 rounded-xl border cursor-pointer transition-all hover:scale-[1.02] ${
                    warMode 
                      ? 'bg-slate-900/80 border-red-500/30 hover:border-red-400' 
                      : 'bg-slate-800/50 border-slate-700 hover:border-cyan-500'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        warMode && (asset.status === 'critical' || asset.status === 'compromised')
                          ? 'bg-red-500/20'
                          : 'bg-cyan-500/20'
                      }`}>
                        <Icon className={`w-5 h-5 ${warMode ? 'text-red-400' : 'text-cyan-400'}`} />
                      </div>
                      <div>
                        <h3 className="font-medium text-white">{asset.name}</h3>
                        <p className={`text-xs ${warMode ? 'text-red-400/60' : 'text-slate-500'}`}>
                          {asset.type.toUpperCase()}
                        </p>
                      </div>
                    </div>
                    <div className={`w-3 h-3 rounded-full ${statusColor}`} />
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className={warMode ? 'text-red-400/60' : 'text-slate-500'}>IP</span>
                      <span className={`font-mono ${warMode ? 'text-red-300' : 'text-cyan-400'}`}>
                        {asset.ip}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className={warMode ? 'text-red-400/60' : 'text-slate-500'}>负责人</span>
                      <span className="text-slate-300">{asset.owner}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className={warMode ? 'text-red-400/60' : 'text-slate-500'}>部门</span>
                      <span className="text-slate-300">{asset.department}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className={warMode ? 'text-red-400/60' : 'text-slate-500'}>风险评分</span>
                      <span className={`font-bold ${getRiskColor(asset.risk_score)}`}>
                        {asset.risk_score}/100
                      </span>
                    </div>
                  </div>

                  {asset.vulnerabilities.length > 0 && (
                    <div className={`mt-3 pt-3 border-t ${
                      warMode ? 'border-red-500/30' : 'border-slate-700'
                    }`}>
                      <div className="flex items-center gap-1 text-xs text-red-400">
                        <AlertTriangle className="w-3 h-3" />
                        <span>{asset.vulnerabilities.length} 个高危漏洞</span>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {assetList.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500">
              <Server className="w-12 h-12 mb-4 opacity-50" />
              <p>没有找到匹配的资产</p>
            </div>
          )}
        </div>

        {/* Footer Stats */}
        <div className={`p-4 border-t flex items-center justify-between ${
          warMode ? 'border-red-500/30' : 'border-slate-700/50'
        }`}>
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-emerald-500 rounded-full" />
              <span className={warMode ? 'text-red-400/60' : 'text-slate-500'}>
                正常: {Object.values(assets).filter(a => a.status === 'normal').length}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-amber-500 rounded-full" />
              <span className={warMode ? 'text-red-400/60' : 'text-slate-500'}>
                警告: {Object.values(assets).filter(a => a.status === 'warning').length}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span className={warMode ? 'text-red-400/60' : 'text-slate-500'}>
                严重: {Object.values(assets).filter(a => a.status === 'critical' || a.status === 'compromised').length}
              </span>
            </div>
          </div>
          
          <button className={`px-4 py-2 rounded-lg text-sm flex items-center gap-2 ${
            warMode 
              ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' 
              : 'bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30'
          }`}>
            <Download className="w-4 h-4" />
            导出资产清单
          </button>
        </div>
      </div>
    </div>
  )
}

// Floating badge for triggering the asset panel
export const AssetPanelFloatingBadge: React.FC<{ onClick: () => void }> = ({ onClick }) => {
  const warMode = useAppStore(state => state.warMode)
  const assetCount = useAppStore(state => Object.keys(state.assets).length)

  return (
    <button
      onClick={onClick}
      className={`fixed right-4 top-20 w-12 h-12 rounded-xl border shadow-lg flex items-center justify-center transition-all hover:scale-110 z-40 ${
        warMode
          ? 'bg-red-500/20 border-red-500/50 text-red-400 hover:border-red-400'
          : 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400 hover:border-cyan-400'
      }`}
    >
      <Server className="w-5 h-5" />
      {assetCount > 0 && (
        <span className={`absolute -top-1 -right-1 w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center ${
          warMode ? 'bg-red-500 text-white' : 'bg-cyan-500 text-white'
        }`}>
          {assetCount}
        </span>
      )}
    </button>
  )
}

export default AssetPanel
