/**
 * CyberSentinel - Alert Panel Component
 * Displays alerts with inline feedback options
 */
import { useEffect, useState } from 'react';
import {
  AlertTriangle,
  AlertCircle,
  AlertOctagon,
  Info,
  Clock,
  ChevronRight,
  Fingerprint,
  ShieldCheck,
  ShieldX,
  X
} from 'lucide-react';
import {
  useAppStore,
  type Alert,
  type AlertLevel
} from '../stores/useAppStore';
import { InlineFeedback } from './FeedbackPanel';

// ==================== Type Definitions ====================

interface AlertCardProps {
  alert: Alert;
  onClick?: () => void;
  warMode: boolean;
}

// ==================== Helper Functions ====================

const getAlertIcon = (level: AlertLevel) => {
  switch (level) {
    case 'critical': return <AlertOctagon className="w-5 h-5" />;
    case 'high': return <AlertTriangle className="w-5 h-5" />;
    case 'medium': return <AlertCircle className="w-5 h-5" />;
    case 'low': return <Info className="w-5 h-5" />;
    default: return <AlertCircle className="w-5 h-5" />;
  }
};

const getAlertColor = (level: AlertLevel, warMode: boolean) => {
  if (warMode) {
    return {
      critical: 'text-red-400 bg-red-500/20 border-red-500/30',
      high: 'text-orange-400 bg-orange-500/20 border-orange-500/30',
      medium: 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30',
      low: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    }[level] || 'text-slate-400 bg-slate-500/20';
  }
  return {
    critical: 'text-red-400 bg-red-500/10 border-red-500/30',
    high: 'text-orange-400 bg-orange-500/10 border-orange-500/30',
    medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
    low: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
  }[level] || 'text-slate-400 bg-slate-500/10';
};

// ==================== Alert Card Component ====================

const AlertCard: React.FC<AlertCardProps> = ({ alert, onClick, warMode }) => {
  const alertColor = getAlertColor(alert.level, warMode);
  const Icon = getAlertIcon(alert.level);

  return (
    <div
      onClick={onClick}
      className={`p-3 rounded-lg border transition-all duration-200 cursor-pointer hover:scale-[1.02] ${
        warMode
          ? 'bg-red-500/5 border-red-500/20 hover:bg-red-500/10'
          : 'bg-slate-800/50 border-slate-700/50 hover:bg-slate-700/50'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${alertColor}`}>
            {Icon}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className={`text-xs px-1.5 py-0.5 rounded ${
                alert.level === 'critical' ? 'bg-red-500/30 text-red-400' :
                alert.level === 'high' ? 'bg-orange-500/30 text-orange-400' :
                alert.level === 'medium' ? 'bg-yellow-500/30 text-yellow-400' :
                'bg-blue-500/30 text-blue-400'
              }`}>
                {alert.level === 'critical' ? '严重' :
                 alert.level === 'high' ? '高危' :
                 alert.level === 'medium' ? '中等' : '低危'}
              </span>
              <span className="text-xs text-slate-500 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {alert.time}
              </span>
            </div>
            <div className={`text-sm font-medium ${warMode ? 'text-red-200' : 'text-white'} truncate`}>
              {alert.type}
            </div>
            <div className="text-xs text-slate-500 mt-1 flex items-center gap-2">
              <span className="flex items-center gap-1">
                <Fingerprint className="w-3 h-3" />
                {alert.source}
              </span>
              <ChevronRight className="w-3 h-3" />
              <span>{alert.target}</span>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-end gap-2">
          <InlineFeedback targetId={alert.id} targetType="ALERT" />
          <span className={`text-xs ${
            alert.confidence >= 90 ? 'text-emerald-400' :
            alert.confidence >= 70 ? 'text-amber-400' : 'text-slate-400'
          }`}>
            {alert.confidence}% 置信度
          </span>
        </div>
      </div>
    </div>
  );
};

// ==================== Main Alert Panel ====================

interface AlertPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AlertPanel: React.FC<AlertPanelProps> = ({ isOpen, onClose }) => {
  const { alerts, setAlerts, warMode, selectAsset } = useAppStore();
  const [filter, setFilter] = useState<AlertLevel | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Initialize alerts from mock data
  useEffect(() => {
    if (alerts.length === 0 && isOpen) {
      setAlerts([
        { id: 'alert-001', level: 'critical', source: '203.0.113.45', target: '10.0.0.25', type: 'SQL注入攻击', time: '14:32:15', mitreTactic: 'T1190', confidence: 95, storylineId: 'story-001', acknowledged: false },
        { id: 'alert-002', level: 'critical', source: '10.0.1.88', target: '10.0.0.30', type: '异常横向移动-暴力破解', time: '14:30:42', mitreTactic: 'T1210', confidence: 88, storylineId: 'story-001', acknowledged: false },
        { id: 'alert-003', level: 'high', source: '10.0.1.88', target: '10.0.0.40', type: '可疑文件传输', time: '14:28:33', mitreTactic: 'T1041', confidence: 76, storylineId: 'story-001', acknowledged: false },
        { id: 'alert-004', level: 'medium', source: '10.0.1.88', target: '8.8.8.8', type: '可疑外联-C2通信', time: '14:25:18', mitreTactic: 'T1071', confidence: 65, storylineId: 'story-001', acknowledged: false },
        { id: 'alert-005', level: 'high', source: '45.33.32.156', target: '10.0.0.1', type: '端口扫描', time: '14:20:00', mitreTactic: 'T1595', confidence: 92, storylineId: 'story-002', acknowledged: false },
      ]);
    }
  }, [alerts.length, isOpen, setAlerts]);

  const filteredAlerts = alerts.filter(alert => {
    const matchesFilter = filter === 'all' || alert.level === filter;
    const matchesSearch = searchTerm === '' ||
      alert.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.source.includes(searchTerm) ||
      alert.target.includes(searchTerm);
    return matchesFilter && matchesSearch;
  });

  const criticalCount = alerts.filter(a => a.level === 'critical').length;
  const highCount = alerts.filter(a => a.level === 'high').length;

  if (!isOpen) return null;

  return (
    <div className={`fixed right-0 top-14 bottom-0 w-[420px] backdrop-blur-xl border-l z-40 flex flex-col transition-all duration-300 ${
      warMode
        ? 'bg-red-950/90 border-red-500/30'
        : 'bg-slate-900/95 border-slate-700/50'
    }`}>
      {/* Header */}
      <div className={`p-4 border-b flex items-center justify-between ${
        warMode ? 'border-red-500/30' : 'border-slate-700/50'
      }`}>
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
            warMode ? 'bg-red-500/20' : 'bg-red-500/20'
          }`}>
            <AlertTriangle className={`w-5 h-5 ${warMode ? 'text-red-400' : 'text-red-400'}`} />
          </div>
          <div>
            <div className="font-semibold text-white flex items-center gap-2">
              安全告警
              {criticalCount > 0 && (
                <span className="px-1.5 py-0.5 text-[10px] bg-red-500 text-white rounded-full animate-pulse">
                  {criticalCount}
                </span>
              )}
            </div>
            <div className="text-xs text-slate-400">实时监控告警列表</div>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-slate-700/50 text-slate-400"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Filters */}
      <div className="p-4 border-b border-slate-700/30 space-y-3">
        {/* Search */}
        <div className="relative">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="搜索告警..."
            className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-300 placeholder-slate-500 focus:outline-none focus:border-red-500"
          />
        </div>

        {/* Level Filter */}
        <div className="flex gap-2">
          {(['all', 'critical', 'high', 'medium', 'low'] as const).map((level) => (
            <button
              key={level}
              onClick={() => setFilter(level)}
              className={`px-3 py-1.5 text-xs rounded-lg transition-colors ${
                filter === level
                  ? level === 'critical' ? 'bg-red-500/30 text-red-400 border border-red-500/50' :
                    level === 'high' ? 'bg-orange-500/30 text-orange-400 border border-orange-500/50' :
                    level === 'medium' ? 'bg-yellow-500/30 text-yellow-400 border border-yellow-500/50' :
                    level === 'low' ? 'bg-blue-500/30 text-blue-400 border border-blue-500/50' :
                    'bg-slate-700 text-white border border-slate-600'
                  : 'bg-slate-800/50 text-slate-400 border border-slate-700/50 hover:bg-slate-700'
              }`}
            >
              {level === 'all' ? '全部' :
               level === 'critical' ? '严重' :
               level === 'high' ? '高危' :
               level === 'medium' ? '中等' : '低危'}
            </button>
          ))}
        </div>
      </div>

      {/* Alert List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {filteredAlerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500">
            <AlertCircle className="w-12 h-12 mb-3 opacity-50" />
            <p className="text-sm">暂无告警</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              warMode={warMode}
              onClick={() => selectAsset(alert.target)}
            />
          ))
        )}
      </div>

      {/* Footer */}
      <div className={`p-4 border-t ${warMode ? 'border-red-500/30' : 'border-slate-700/50'}`}>
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>共 {filteredAlerts.length} 条告警</span>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-red-500" />
              {criticalCount} 严重
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-orange-500" />
              {highCount} 高危
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== Floating Badge ====================

export const AlertPanelFloatingBadge: React.FC<{ onClick: () => void; alertCount: number }> = ({ onClick, alertCount }) => {
  if (alertCount === 0) return null;

  return (
    <button
      onClick={onClick}
      className="fixed right-4 top-20 w-14 h-14 rounded-full bg-gradient-to-r from-red-500 to-orange-500 text-white shadow-lg flex items-center justify-center hover:scale-110 transition-transform z-40 animate-pulse"
    >
      <AlertTriangle className="w-6 h-6" />
      <span className="absolute -top-1 -right-1 w-5 h-5 bg-white text-red-500 text-xs font-bold rounded-full flex items-center justify-center">
        {alertCount}
      </span>
    </button>
  );
};

export default AlertPanel;
