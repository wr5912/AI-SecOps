/**
 * AISecOps - Unified Notification Panel
 * Combines alerts and approval requests in one place
 */
import { useState, useMemo } from 'react';
import {
  Bell,
  Shield,
  AlertTriangle,
  AlertCircle,
  AlertOctagon,
  Info,
  Clock,
  ChevronRight,
  Fingerprint,
  X,
  Check,
  Lock,
  Ban,
  FileCode,
  HardDrive,
  User,
  Filter,
  Search,
  RefreshCw,
  ChevronDown,
  CheckCircle,
  XCircle,
  ShieldCheck,
  ShieldAlert
} from 'lucide-react';
import {
  useAppStore,
  type Alert,
  type AlertLevel,
  type ApprovalRequest,
  type ApprovalStatus
} from '../stores/useAppStore';
import { InlineFeedback } from './FeedbackPanel';

// ==================== Type Definitions ====================

type NotificationType = 'alert' | 'approval';

interface NotificationItem {
  id: string;
  type: NotificationType;
  timestamp: string;
  priority: AlertLevel | ApprovalRequest['priority'];
}

interface NotificationPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

// ==================== Helper Functions ====================

const getAlertIcon = (level: AlertLevel) => {
  switch (level) {
    case 'critical': return <AlertOctagon className="w-4 h-4" />;
    case 'high': return <AlertTriangle className="w-4 h-4" />;
    case 'medium': return <AlertCircle className="w-4 h-4" />;
    case 'low': return <Info className="w-4 h-4" />;
    default: return <AlertCircle className="w-4 h-4" />;
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

const actionConfigs = [
  { type: 'isolation' as const, label: '主机隔离', icon: <Lock className="w-4 h-4" />, color: 'text-red-400', bgColor: 'bg-red-500/20' },
  { type: 'block_ip' as const, label: 'IP封禁', icon: <Ban className="w-4 h-4" />, color: 'text-orange-400', bgColor: 'bg-orange-500/20' },
  { type: 'quarantine' as const, label: '隔离文件', icon: <HardDrive className="w-4 h-4" />, color: 'text-purple-400', bgColor: 'bg-purple-500/20' },
  { type: 'script_execution' as const, label: '脚本执行', icon: <FileCode className="w-4 h-4" />, color: 'text-cyan-400', bgColor: 'bg-cyan-500/20' },
];

const getActionConfig = (type: ApprovalRequest['type']) => {
  return actionConfigs.find((a) => a.type === type) || actionConfigs[0];
};

const getPriorityColor = (priority: string): string => {
  switch (priority) {
    case 'critical': return 'text-red-400 bg-red-500/20';
    case 'high': return 'text-orange-400 bg-orange-500/20';
    case 'medium': return 'text-yellow-400 bg-yellow-500/20';
    case 'low': return 'text-blue-400 bg-blue-500/20';
    default: return 'text-slate-400 bg-slate-500/20';
  }
};

const getStatusBadge = (status: ApprovalStatus) => {
  switch (status) {
    case 'pending':
      return (
        <span className="flex items-center gap-1 px-2 py-0.5 text-xs bg-yellow-500/20 text-yellow-400 rounded-full">
          <Clock className="w-3 h-3" />
          待审批
        </span>
      );
    case 'approved':
      return (
        <span className="flex items-center gap-1 px-2 py-0.5 text-xs bg-emerald-500/20 text-emerald-400 rounded-full">
          <CheckCircle className="w-3 h-3" />
          已批准
        </span>
      );
    case 'rejected':
      return (
        <span className="flex items-center gap-1 px-2 py-0.5 text-xs bg-red-500/20 text-red-400 rounded-full">
          <XCircle className="w-3 h-3" />
          已拒绝
        </span>
      );
    default:
      return null;
  }
};

// ==================== Main Component ====================

export const NotificationPanel: React.FC<NotificationPanelProps> = ({ isOpen, onClose }) => {
  const {
    alerts,
    pendingApprovals,
    approveRequest,
    rejectRequest,
    currentUser,
    warMode,
    selectAsset
  } = useAppStore();

  const [activeTab, setActiveTab] = useState<'all' | 'alerts' | 'approvals'>('all');
  const [alertFilter, setAlertFilter] = useState<AlertLevel | 'all'>('all');
  const [approvalFilter, setApprovalFilter] = useState<ApprovalStatus | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(null);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  // Combine alerts and approvals into unified list
  const allNotifications = useMemo(() => {
    const items: Array<Alert & { notificationType: 'alert' } | ApprovalRequest & { notificationType: 'approval' }> = [
      ...alerts.map(a => ({ ...a, notificationType: 'alert' as const })),
      ...pendingApprovals.map(a => ({ ...a, notificationType: 'approval' as const }))
    ];
    
    // Sort by priority and timestamp
    return items.sort((a, b) => {
      const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      const aPriority = a.notificationType === 'alert' ? priorityOrder[a.severity as keyof typeof priorityOrder] || 3 : priorityOrder[a.priority as keyof typeof priorityOrder] || 3;
      const bPriority = b.notificationType === 'alert' ? priorityOrder[b.severity as keyof typeof priorityOrder] || 3 : priorityOrder[b.priority as keyof typeof priorityOrder] || 3;
      return aPriority - bPriority;
    });
  }, [alerts, pendingApprovals]);

  // Filter notifications
  const filteredNotifications = allNotifications.filter(item => {
    // Tab filter
    if (activeTab === 'alerts' && item.notificationType !== 'alert') return false;
    if (activeTab === 'approvals' && item.notificationType !== 'approval') return false;
    
    // Alert level filter
    if (item.notificationType === 'alert' && alertFilter !== 'all' && item.severity !== alertFilter) return false;
    
    // Approval status filter  
    if (item.notificationType === 'approval' && approvalFilter !== 'all' && item.status !== approvalFilter) return false;
    
    // Search filter
    if (searchTerm) {
      if (item.notificationType === 'alert') {
        const matches = item.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.attacker_ip?.includes(searchTerm) ||
          item.victim_ip?.includes(searchTerm);
        if (!matches) return false;
      } else {
        const matches = item.target.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.description.toLowerCase().includes(searchTerm.toLowerCase());
        if (!matches) return false;
      }
    }
    
    return true;
  });

  const alertCount = alerts.filter(a => !a.acknowledged).length;
  const approvalCount = pendingApprovals.filter(r => r.status === 'pending').length;
  const criticalAlertCount = alerts.filter(a => a.severity === 'critical').length;

  // Approval handlers
  const handleApprove = (request: ApprovalRequest) => {
    if (!currentUser) return;
    approveRequest(request.id, currentUser.name);
    useAppStore.getState().addNotification({
      message: `已批准 ${request.type} 请求`,
      type: 'success',
    });
  };

  const handleReject = () => {
    if (!selectedApproval || !currentUser) return;
    rejectRequest(selectedApproval.id, currentUser.name);
    setShowRejectModal(false);
    setSelectedApproval(null);
    setRejectReason('');
    useAppStore.getState().addNotification({
      message: `已拒绝 ${selectedApproval.type} 请求`,
      type: 'info',
    });
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Notification Panel */}
      <div className={`fixed right-0 top-14 bottom-0 w-[480px] backdrop-blur-xl border-l z-50 flex flex-col transition-all duration-300 ${
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
              warMode ? 'bg-red-500/20' : 'bg-cyan-500/20'
            }`}>
              <Bell className={`w-5 h-5 ${warMode ? 'text-red-400' : 'text-cyan-400'}`} />
            </div>
            <div>
              <div className="font-semibold text-white flex items-center gap-2">
                通知中心
                {(alertCount + approvalCount) > 0 && (
                  <span className="px-1.5 py-0.5 text-[10px] bg-red-500 text-white rounded-full animate-pulse">
                    {alertCount + approvalCount}
                  </span>
                )}
              </div>
              <div className="text-xs text-slate-400">告警与审批消息</div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-700/50 text-slate-400"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className={`p-4 border-b ${warMode ? 'border-red-500/30' : 'border-slate-700/50'}`}>
          <div className="flex gap-2 mb-3">
            {(['all', 'alerts', 'approvals'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 px-3 py-2 text-sm rounded-lg transition-colors flex items-center justify-center gap-2 ${
                  activeTab === tab
                    ? warMode
                      ? 'bg-red-500/30 text-red-400 border border-red-500/50'
                      : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                    : 'bg-slate-800/50 text-slate-400 border border-slate-700/50 hover:bg-slate-700'
                }`}
              >
                {tab === 'all' && '全部'}
                {tab === 'alerts' && (
                  <>
                    <AlertTriangle className="w-4 h-4" />
                    告警 {alertCount > 0 && `(${alertCount})`}
                  </>
                )}
                {tab === 'approvals' && (
                  <>
                    <Shield className="w-4 h-4" />
                    审批 {approvalCount > 0 && `(${approvalCount})`}
                  </>
                )}
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="搜索通知内容..."
              className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-300 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Notification List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {filteredNotifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Bell className="w-12 h-12 mb-3 opacity-50" />
              <p className="text-sm">暂无通知</p>
            </div>
          ) : (
            filteredNotifications.map((item) => {
              if (item.notificationType === 'alert') {
                const alert = item as Alert & { notificationType: 'alert' };
                const alertColor = getAlertColor(alert.severity, warMode);
                const AlertIcon = getAlertIcon(alert.severity);
                
                return (
                  <div
                    key={alert.id}
                    onClick={() => selectAsset(alert.victim_ip)}
                    className={`p-4 rounded-xl border transition-all duration-200 cursor-pointer hover:scale-[1.01] ${
                      warMode
                        ? 'bg-red-500/10 border-red-500/30 hover:border-red-500/50'
                        : 'bg-slate-800/50 border-slate-700/50 hover:border-cyan-500/30'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className={`p-2 rounded-lg ${alertColor}`}>
                          {AlertIcon}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className={`text-xs px-1.5 py-0.5 rounded ${
                              alert.severity === 'critical' ? 'bg-red-500/30 text-red-400' :
                              alert.severity === 'high' ? 'bg-orange-500/30 text-orange-400' :
                              alert.severity === 'medium' ? 'bg-yellow-500/30 text-yellow-400' :
                              'bg-blue-500/30 text-blue-400'
                            }`}>
                              {alert.severity === 'critical' ? '严重' :
                               alert.severity === 'high' ? '高危' :
                               alert.severity === 'medium' ? '中等' : '低危'}
                            </span>
                            <span className="text-xs text-slate-500 flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {alert.time}
                            </span>
                          </div>
                          <div className={`text-sm font-medium mt-1 ${warMode ? 'text-red-200' : 'text-white'}`}>
                            {alert.type}
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-xs text-slate-500 flex items-center gap-2 mb-2">
                      <span className="flex items-center gap-1">
                        <Fingerprint className="w-3 h-3" />
                        {alert.attacker_ip}
                      </span>
                      <ChevronRight className="w-3 h-3" />
                      <span>{alert.victim_ip}</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <InlineFeedback targetId={alert.id} targetType="ALERT" />
                      <span className={`text-xs ${
                        (alert as any).confidence_score >= 90 ? 'text-emerald-400' :
                        (alert as any).confidence_score >= 70 ? 'text-amber-400' : 'text-slate-400'
                      }`}>
                        {(alert as any).confidence_score}% 置信度
                      </span>
                    </div>
                  </div>
                );
              } else {
                const approval = item as ApprovalRequest & { notificationType: 'approval' };
                const actionConfig = getActionConfig(approval.type);
                
                return (
                  <div
                    key={approval.id}
                    className={`p-4 rounded-xl border transition-all duration-200 ${
                      warMode
                        ? 'bg-red-500/10 border-red-500/30 hover:border-red-500/50'
                        : 'bg-slate-800/50 border-slate-700/50 hover:border-amber-500/30'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${actionConfig.bgColor}`}>
                          {actionConfig.icon}
                        </div>
                        <div>
                          <div className={`text-sm font-medium ${actionConfig.color}`}>
                            {actionConfig.label}
                          </div>
                          <div className="text-xs text-slate-500">{approval.id}</div>
                        </div>
                      </div>
                      {getStatusBadge(approval.status)}
                    </div>
                    
                    <div className="text-xs text-slate-400 mb-2">
                      目标: <span className="text-white font-mono">{approval.target}</span>
                    </div>
                    <div className="text-xs text-slate-500 line-clamp-2 mb-2">{approval.description}</div>
                    
                    <div className="flex items-center justify-between text-xs text-slate-500 mb-3">
                      <div className="flex items-center gap-3">
                        <span className="flex items-center gap-1">
                          <User className="w-3 h-3" />
                          {approval.requester}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {approval.requestTime}
                        </span>
                      </div>
                      <span className={`px-2 py-0.5 rounded ${getPriorityColor(approval.priority)}`}>
                        {approval.priority === 'critical' ? '紧急' :
                         approval.priority === 'high' ? '高' :
                         approval.priority === 'medium' ? '中' : '低'}
                      </span>
                    </div>
                    
                    {approval.status === 'pending' && (
                      <div className="flex gap-2 pt-2 border-t border-slate-700/30">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleApprove(approval);
                          }}
                          className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 rounded-lg transition-colors"
                        >
                          <Check className="w-4 h-4" />
                          批准
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedApproval(approval);
                            setShowRejectModal(true);
                          }}
                          className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors"
                        >
                          <X className="w-4 h-4" />
                          拒绝
                        </button>
                      </div>
                    )}
                  </div>
                );
              }
            })
          )}
        </div>

        {/* Footer */}
        <div className={`p-4 border-t ${warMode ? 'border-red-500/30' : 'border-slate-700/50'}`}>
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>
              共 {filteredNotifications.length} 条通知
              {criticalAlertCount > 0 && ` · ${criticalAlertCount} 严重告警`}
            </span>
            <button className="flex items-center gap-1 hover:text-white transition-colors">
              <RefreshCw className="w-3 h-3" />
              刷新
            </button>
          </div>
        </div>
      </div>

      {/* Reject Modal */}
      {showRejectModal && selectedApproval && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[60]">
          <div className="w-[400px] bg-slate-900 border border-slate-700 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center">
                <AlertOctagon className="w-5 h-5 text-red-400" />
              </div>
              <div>
                <div className="font-semibold text-white">拒绝审批请求</div>
                <div className="text-xs text-slate-400">{selectedApproval.id}</div>
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm text-slate-400 mb-2">拒绝原因</label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="请输入拒绝原因..."
                className="w-full h-24 px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-300 placeholder-slate-500 focus:outline-none focus:border-red-500 resize-none"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setSelectedApproval(null);
                  setRejectReason('');
                }}
                className="flex-1 px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleReject}
                className="flex-1 px-4 py-2 text-sm bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
              >
                确认拒绝
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

// ==================== Notification Badge in Header ====================

export const NotificationBadge: React.FC<{ onClick: () => void }> = ({ onClick }) => {
  const alertCount = useAppStore((state) => 
    state.alerts.filter(a => !a.acknowledged).length
  );
  const approvalCount = useAppStore((state) => 
    state.pendingApprovals.filter(r => r.status === 'pending').length
  );
  const warMode = useAppStore((state) => state.warMode);
  
  const totalCount = alertCount + approvalCount;

  return (
    <button
      onClick={onClick}
      className={`relative p-2 rounded-lg transition-colors ${
        totalCount > 0
          ? warMode
            ? 'hover:bg-red-500/30 text-red-400'
            : 'hover:bg-cyan-500/20 text-cyan-400'
          : 'hover:bg-slate-700/50 text-slate-400'
      }`}
    >
      <Bell className="w-5 h-5" />
      {totalCount > 0 && (
        <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
      )}
    </button>
  );
};

export default NotificationPanel;
