/**
 * AISecOps - HITL (Human In The Loop) Approval Panel
 * Following FRONTEND_DESIGN_DOCUMENT.md Chapter 10.3
 *
 * Security-critical operations require human approval before execution:
 * - Network isolation
 * - IP blocking
 * - Script execution
 * - Quarantine actions
 */

import { useState } from 'react';
import {
  Shield,
  X,
  Check,
  AlertTriangle,
  Lock,
  Ban,
  FileCode,
  HardDrive,
  Clock,
  User,
  Filter,
  Search,
  RefreshCw,
  ChevronDown,
  AlertOctagon,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { useAppStore, type ApprovalRequest, type ApprovalStatus } from '../stores/useAppStore';

// ==================== Type Definitions ====================

interface ApprovalAction {
  type: ApprovalRequest['type'];
  label: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}

// Action type configurations
const actionConfigs: ApprovalAction[] = [
  { type: 'isolation', label: '主机隔离', icon: <Lock className="w-4 h-4" />, color: 'text-red-400', bgColor: 'bg-red-500/20' },
  { type: 'block_ip', label: 'IP封禁', icon: <Ban className="w-4 h-4" />, color: 'text-orange-400', bgColor: 'bg-orange-500/20' },
  { type: 'quarantine', label: '隔离文件', icon: <HardDrive className="w-4 h-4" />, color: 'text-purple-400', bgColor: 'bg-purple-500/20' },
  { type: 'script_execution', label: '脚本执行', icon: <FileCode className="w-4 h-4" />, color: 'text-cyan-400', bgColor: 'bg-cyan-500/20' },
];

// ==================== Helper Functions ====================

const getActionConfig = (type: ApprovalRequest['type']): ApprovalAction => {
  return actionConfigs.find((a) => a.type === type) || actionConfigs[0];
};

const getPriorityColor = (priority: ApprovalRequest['priority']): string => {
  switch (priority) {
    case 'critical': return 'text-red-400 bg-red-500/20';
    case 'high': return 'text-orange-400 bg-orange-500/20';
    case 'medium': return 'text-yellow-400 bg-yellow-500/20';
    case 'low': return 'text-blue-400 bg-blue-500/20';
    default: return 'text-slate-400 bg-slate-500/20';
  }
};

const getStatusBadge = (status: ApprovalStatus): React.ReactNode => {
  switch (status) {
    case 'pending':
      return (
        <span className="flex items-center gap-1 px-2 py-1 text-xs bg-yellow-500/20 text-yellow-400 rounded-full">
          <Clock className="w-3 h-3" />
          待审批
        </span>
      );
    case 'approved':
      return (
        <span className="flex items-center gap-1 px-2 py-1 text-xs bg-emerald-500/20 text-emerald-400 rounded-full">
          <CheckCircle className="w-3 h-3" />
          已批准
        </span>
      );
    case 'rejected':
      return (
        <span className="flex items-center gap-1 px-2 py-1 text-xs bg-red-500/20 text-red-400 rounded-full">
          <XCircle className="w-3 h-3" />
          已拒绝
        </span>
      );
    default:
      return null;
  }
};

// ==================== Main Component ====================

interface HITLApprovalPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HITLApprovalPanel: React.FC<HITLApprovalPanelProps> = ({ isOpen, onClose }) => {
  const {
    pendingApprovals,
    approveRequest,
    rejectRequest,
    currentUser,
    warMode
  } = useAppStore();

  const [filter, setFilter] = useState<ApprovalStatus | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState<ApprovalRequest['type'] | 'all'>('all');
  const [selectedRequest, setSelectedRequest] = useState<ApprovalRequest | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);

  // Filter approvals
  const filteredApprovals = pendingApprovals.filter((req) => {
    const matchesStatus = filter === 'all' || req.status === filter;
    const matchesAction = actionFilter === 'all' || req.type === actionFilter;
    const matchesSearch = searchTerm === '' ||
      req.target.toLowerCase().includes(searchTerm.toLowerCase()) ||
      req.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesAction && matchesSearch;
  });

  const pendingCount = pendingApprovals.filter((r) => r.status === 'pending').length;

  // Handle approval
  const handleApprove = (request: ApprovalRequest) => {
    if (!currentUser) return;
    approveRequest(request.id, currentUser.name);
    useAppStore.getState().addNotification({
      message: `已批准 ${request.type} 请求`,
      type: 'success',
    });
  };

  // Handle rejection
  const handleReject = () => {
    if (!selectedRequest || !currentUser) return;
    rejectRequest(selectedRequest.id, currentUser.name);
    setShowRejectModal(false);
    setSelectedRequest(null);
    setRejectReason('');
    useAppStore.getState().addNotification({
      message: `已拒绝 ${selectedRequest.type} 请求`,
      type: 'info',
    });
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Panel */}
      <div className={`fixed right-0 top-14 bottom-0 w-[480px] backdrop-blur-xl border-l z-40 flex flex-col transition-all duration-300 ${
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
              warMode ? 'bg-red-500/20' : 'bg-amber-500/20'
            }`}>
              <Shield className={`w-5 h-5 ${warMode ? 'text-red-400' : 'text-amber-400'}`} />
            </div>
            <div>
              <div className="font-semibold text-white flex items-center gap-2">
                审批队列
                {pendingCount > 0 && (
                  <span className="px-1.5 py-0.5 text-[10px] bg-red-500 text-white rounded-full animate-pulse">
                    {pendingCount}
                  </span>
                )}
              </div>
              <div className="text-xs text-slate-400">人工确认关键操作</div>
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
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="搜索目标、描述..."
              className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-300 placeholder-slate-500 focus:outline-none focus:border-amber-500"
            />
          </div>

          {/* Filter Row */}
          <div className="flex gap-2">
            {/* Status Filter */}
            <div className="relative flex-1">
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as ApprovalStatus | 'all')}
                className="w-full appearance-none px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-300 focus:outline-none focus:border-amber-500 cursor-pointer"
              >
                <option value="all">全部状态</option>
                <option value="pending">待审批</option>
                <option value="approved">已批准</option>
                <option value="rejected">已拒绝</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
            </div>

            {/* Action Filter */}
            <div className="relative flex-1">
              <select
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value as ApprovalRequest['type'] | 'all')}
                className="w-full appearance-none px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-300 focus:outline-none focus:border-amber-500 cursor-pointer"
              >
                <option value="all">全部操作</option>
                {actionConfigs.map((config) => (
                  <option key={config.type} value={config.type}>
                    {config.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Approval List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {filteredApprovals.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Shield className="w-12 h-12 mb-3 opacity-50" />
              <p className="text-sm">暂无审批请求</p>
            </div>
          ) : (
            filteredApprovals.map((request) => {
              const actionConfig = getActionConfig(request.type);
              return (
                <div
                  key={request.id}
                  className={`p-4 rounded-xl border transition-all duration-200 cursor-pointer ${
                    warMode
                      ? 'bg-red-500/10 border-red-500/30 hover:border-red-500/50'
                      : 'bg-slate-800/50 border-slate-700/50 hover:border-amber-500/50'
                  } ${selectedRequest?.id === request.id ? 'ring-2 ring-amber-500' : ''}`}
                  onClick={() => setSelectedRequest(request)}
                >
                  {/* Request Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${actionConfig.bgColor}`}>
                        {actionConfig.icon}
                      </div>
                      <div>
                        <div className={`text-sm font-medium ${actionConfig.color}`}>
                          {actionConfig.label}
                        </div>
                        <div className="text-xs text-slate-500">{request.id}</div>
                      </div>
                    </div>
                    {getStatusBadge(request.status)}
                  </div>

                  {/* Request Details */}
                  <div className="space-y-2 mb-3">
                    <div className="flex items-center gap-2 text-xs">
                      <AlertTriangle className="w-3 h-3 text-slate-500" />
                      <span className="text-slate-400">目标:</span>
                      <span className="text-white font-mono">{request.target}</span>
                    </div>
                    <div className="text-xs text-slate-400 line-clamp-2">{request.description}</div>
                  </div>

                  {/* Request Meta */}
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center gap-1">
                        <User className="w-3 h-3" />
                        {request.requester}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {request.requestTime}
                      </span>
                    </div>
                    <span className={`px-2 py-0.5 rounded ${getPriorityColor(request.priority)}`}>
                      {request.priority === 'critical' ? '紧急' :
                       request.priority === 'high' ? '高' :
                       request.priority === 'medium' ? '中' : '低'}
                    </span>
                  </div>

                  {/* Action Buttons */}
                  {request.status === 'pending' && (
                    <div className="flex gap-2 mt-3 pt-3 border-t border-slate-700/30">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleApprove(request);
                        }}
                        className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 rounded-lg transition-colors"
                      >
                        <Check className="w-4 h-4" />
                        批准
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedRequest(request);
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
            })
          )}
        </div>

        {/* Footer */}
        <div className={`p-4 border-t ${warMode ? 'border-red-500/30' : 'border-slate-700/50'}`}>
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>共 {filteredApprovals.length} 条请求</span>
            <button className="flex items-center gap-1 hover:text-white transition-colors">
              <RefreshCw className="w-3 h-3" />
              刷新
            </button>
          </div>
        </div>
      </div>

      {/* Reject Modal */}
      {showRejectModal && selectedRequest && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="w-[400px] bg-slate-900 border border-slate-700 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center">
                <AlertOctagon className="w-5 h-5 text-red-400" />
              </div>
              <div>
                <div className="font-semibold text-white">拒绝审批请求</div>
                <div className="text-xs text-slate-400">{selectedRequest.id}</div>
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
                  setSelectedRequest(null);
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

// ==================== Floating Badge ====================

export const HITLFloatingBadge: React.FC<{ onClick: () => void }> = ({ onClick }) => {
  const pendingCount = useAppStore((state) =>
    state.pendingApprovals.filter((r) => r.status === 'pending').length
  );
  const warMode = useAppStore((state) => state.warMode);

  if (pendingCount === 0) return null;

  return (
    <button
      onClick={onClick}
      className={`fixed right-4 top-20 w-14 h-14 rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform z-40 ${
        warMode
          ? 'bg-gradient-to-r from-red-500 to-orange-500 animate-pulse'
          : 'bg-gradient-to-r from-amber-500 to-orange-500'
      }`}
    >
      <Shield className="w-6 h-6 text-white" />
      <span className="absolute -top-1 -right-1 w-5 h-5 bg-white text-slate-900 text-xs font-bold rounded-full flex items-center justify-center">
        {pendingCount}
      </span>
    </button>
  );
};

export default HITLApprovalPanel;
