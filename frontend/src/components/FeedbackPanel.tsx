/**
 * AISecOps - Feedback Collection Component
 * Following FRONTEND_DESIGN_DOCUMENT.md Chapter 10.4
 *
 * Collects user feedback on:
 * - AI suggestions accuracy
 * - Alert classification quality
 * - Storyline detection accuracy
 * - General system improvements
 */

import { useState } from 'react';
import {
  MessageSquare,
  X,
  Send,
  ThumbsUp,
  ThumbsDown,
  Star,
  AlertCircle,
  Brain,
  GitBranch,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Check,
  ShieldCheck,
  ShieldX,
  ThumbsUpIcon,
  ThumbsDownIcon,
  AlertTriangle,
  XCircle,
  CheckCircle
} from 'lucide-react';
import {
  useAppStore,
  type FeedbackEntry,
  type FeedbackActionType,
  type FeedbackTargetType
} from '../stores/useAppStore';

// ==================== Type Definitions ====================

// Feedback action configurations based on target type
interface FeedbackActionConfig {
  action: FeedbackActionType;
  label: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}

// Context-specific feedback actions
const alertFeedbackActions: FeedbackActionConfig[] = [
  { action: 'TRUE_POSITIVE', label: '确认真实', icon: <ShieldCheck className="w-3.5 h-3.5" />, color: 'text-emerald-400', bgColor: 'bg-emerald-500/20' },
  { action: 'FALSE_POSITIVE', label: '误报', icon: <ShieldX className="w-3.5 h-3.5" />, color: 'text-amber-400', bgColor: 'bg-amber-500/20' },
];

const storylineFeedbackActions: FeedbackActionConfig[] = [
  { action: 'AI_CORRECT', label: '关联准确', icon: <CheckCircle className="w-3.5 h-3.5" />, color: 'text-emerald-400', bgColor: 'bg-emerald-500/20' },
  { action: 'AI_INCORRECT', label: '关联错误', icon: <XCircle className="w-3.5 h-3.5" />, color: 'text-red-400', bgColor: 'bg-red-500/20' },
];

const aiFeedbackActions: FeedbackActionConfig[] = [
  { action: 'THUMBS_UP', label: '有帮助', icon: <ThumbsUpIcon className="w-3.5 h-3.5" />, color: 'text-emerald-400', bgColor: 'bg-emerald-500/20' },
  { action: 'THUMBS_DOWN', label: '没帮助', icon: <ThumbsDownIcon className="w-3.5 h-3.5" />, color: 'text-red-400', bgColor: 'bg-red-500/20' },
  { action: 'AI_CORRECT', label: '正确', icon: <Check className="w-3.5 h-3.5" />, color: 'text-cyan-400', bgColor: 'bg-cyan-500/20' },
  { action: 'AI_INCORRECT', label: '修正', icon: <AlertTriangle className="w-3.5 h-3.5" />, color: 'text-amber-400', bgColor: 'bg-amber-500/20' },
];

// ==================== Inline Feedback Component ====================

interface InlineFeedbackProps {
  targetId: string;
  targetType: FeedbackTargetType;
  onFeedbackSubmit?: (feedback: FeedbackEntry) => void;
}

export const InlineFeedback: React.FC<InlineFeedbackProps> = ({
  targetId,
  targetType,
  onFeedbackSubmit
}) => {
  const { quickFeedback, setQuickFeedback, addFeedback, addNotification } = useAppStore();

  const currentFeedback = quickFeedback[targetId];

  // Get feedback actions based on target type
  const getFeedbackActions = (): FeedbackActionConfig[] => {
    switch (targetType) {
      case 'ALERT':
        return alertFeedbackActions;
      case 'STORYLINE':
        return storylineFeedbackActions;
      case 'DISPOSAL_RECOMMENDATION':
        return aiFeedbackActions;
      default:
        return aiFeedbackActions;
    }
  };

  const feedbackActions = getFeedbackActions();

  const handleFeedback = (action: FeedbackActionType) => {
    // Toggle feedback if already selected
    if (currentFeedback === action) {
      setQuickFeedback(targetId, action);
    }

    // Create feedback entry
    const feedback: FeedbackEntry = {
      id: `fb-${Date.now()}`,
      type: targetType,
      action,
      targetId,
      timestamp: new Date().toISOString(),
    };

    // Update quick feedback state (optimistic UI)
    setQuickFeedback(targetId, action);

    // Add to feedback entries
    addFeedback(feedback);

    // Show notification
    const actionLabel = feedbackActions.find(a => a.action === action)?.label || action;
    addNotification({
      message: `已提交反馈: ${actionLabel}`,
      type: 'success',
    });

    // Callback
    onFeedbackSubmit?.(feedback);
  };

  return (
    <div className="flex items-center gap-1">
      {feedbackActions.map((config) => (
        <button
          key={config.action}
          onClick={() => handleFeedback(config.action)}
          className={`flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-all duration-200 ${
            currentFeedback === config.action
              ? `${config.bgColor} ${config.color} border border-current`
              : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700 hover:text-white border border-transparent'
          }`}
          title={config.label}
        >
          {config.icon}
          <span className="hidden sm:inline">{config.label}</span>
        </button>
      ))}
    </div>
  );
};

// ==================== Star Rating Component ====================

const StarRating: React.FC<{
  rating: number;
  onChange: (rating: number) => void;
  size?: 'sm' | 'md';
}> = ({ rating, onChange, size = 'md' }) => {
  const stars = [1, 2, 3, 4, 5];
  const starSize = size === 'sm' ? 'w-4 h-4' : 'w-6 h-6';
  const starGap = size === 'sm' ? 'gap-1' : 'gap-2';

  return (
    <div className={`flex ${starGap}`}>
      {stars.map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => onChange(star)}
          className={`transition-transform hover:scale-110 ${rating >= star ? 'text-amber-400' : 'text-slate-600 hover:text-slate-500'}`}
        >
          <Star className={`${starSize} ${rating >= star ? 'fill-current' : ''}`} />
        </button>
      ))}
    </div>
  );
};

// ==================== Main Feedback Panel ====================

interface FeedbackPanelProps {
  isOpen: boolean;
  onClose: () => void;
  contextId?: string;
  contextType?: FeedbackTargetType;
}

export const FeedbackPanel: React.FC<FeedbackPanelProps> = ({
  isOpen,
  onClose,
  contextId,
  contextType = 'ALERT'
}) => {
  const { addFeedback, currentTraceId, quickFeedback, setQuickFeedback } = useAppStore();

  const [feedbackType] = useState<FeedbackTargetType>(contextType);
  const [rating, setRating] = useState<5 | 1 | 2 | 3 | 4>(5);
  const [comment, setComment] = useState('');
  const [sentiment, setSentiment] = useState<'positive' | 'neutral' | 'negative' | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  // Handle submit
  const handleSubmit = () => {
    const action: FeedbackActionType = sentiment === 'positive' ? 'THUMBS_UP' :
      sentiment === 'negative' ? 'THUMBS_DOWN' : 'AI_CORRECT';

    const feedback: FeedbackEntry = {
      id: `fb-${Date.now()}`,
      type: feedbackType,
      action,
      targetId: contextId || 'general',
      rating,
      comment: comment.trim() || undefined,
      timestamp: new Date().toISOString(),
      traceId: currentTraceId || undefined,
    };

    addFeedback(feedback);
    if (contextId) {
      setQuickFeedback(contextId, action);
    }
    setSubmitted(true);

    // Reset after delay
    setTimeout(() => {
      setSubmitted(false);
      setRating(5);
      setComment('');
      setSentiment(null);
      onClose();
    }, 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed right-0 top-14 bottom-0 w-[400px] backdrop-blur-xl border-l border-slate-700/50 bg-slate-900/95 flex flex-col z-40">
      {/* Header */}
      <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
            <MessageSquare className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-semibold text-white">反馈建议</div>
            <div className="text-xs text-slate-400">帮助我们改进系统</div>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 rounded-lg hover:bg-slate-700/50 text-slate-400"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {submitted ? (
          // Success State
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center mb-4">
              <Check className="w-8 h-8 text-emerald-400" />
            </div>
            <div className="text-lg font-semibold text-white mb-2">感谢您的反馈</div>
            <div className="text-sm text-slate-400">
              您的意见对我们非常重要
            </div>
          </div>
        ) : (
          <>
            {/* Target Type Display */}
            <div>
              <label className="block text-sm text-slate-400 mb-3">反馈对象</label>
              <div className={`p-4 rounded-lg border ${
                feedbackType === 'ALERT' ? 'bg-red-500/10 border-red-500/30' :
                feedbackType === 'STORYLINE' ? 'bg-cyan-500/10 border-cyan-500/30' :
                'bg-purple-500/10 border-purple-500/30'
              }`}>
                <div className="flex items-center gap-2">
                  {feedbackType === 'ALERT' && <AlertCircle className="w-5 h-5 text-red-400" />}
                  {feedbackType === 'STORYLINE' && <GitBranch className="w-5 h-5 text-cyan-400" />}
                  {feedbackType === 'DISPOSAL_RECOMMENDATION' && <Brain className="w-5 h-5 text-purple-400" />}
                  <span className="text-sm font-medium text-white">
                    {feedbackType === 'ALERT' ? '告警反馈' :
                     feedbackType === 'STORYLINE' ? '故事线反馈' : '处置建议反馈'}
                  </span>
                </div>
                {contextId && (
                  <div className="text-xs text-slate-400 mt-1">
                    ID: {contextId}
                  </div>
                )}
              </div>
            </div>

            {/* Sentiment Quick Actions */}
            <div>
              <label className="block text-sm text-slate-400 mb-3">快速评价</label>
              <div className="flex gap-3">
                <button
                  onClick={() => setSentiment('positive')}
                  className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border transition-all ${
                    sentiment === 'positive'
                      ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400'
                      : 'bg-slate-800/50 border-slate-700/50 text-slate-400 hover:border-emerald-500/30'
                  }`}
                >
                  <ThumbsUp className="w-5 h-5" />
                  <span className="text-sm">有帮助</span>
                </button>
                <button
                  onClick={() => setSentiment('neutral')}
                  className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border transition-all ${
                    sentiment === 'neutral'
                      ? 'bg-amber-500/20 border-amber-500/50 text-amber-400'
                      : 'bg-slate-800/50 border-slate-700/50 text-slate-400 hover:border-amber-500/30'
                  }`}
                >
                  <MessageSquare className="w-5 h-5" />
                  <span className="text-sm">一般</span>
                </button>
                <button
                  onClick={() => setSentiment('negative')}
                  className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border transition-all ${
                    sentiment === 'negative'
                      ? 'bg-red-500/20 border-red-500/50 text-red-400'
                      : 'bg-slate-800/50 border-slate-700/50 text-slate-400 hover:border-red-500/30'
                  }`}
                >
                  <ThumbsDown className="w-5 h-5" />
                  <span className="text-sm">不满意</span>
                </button>
              </div>
            </div>

            {/* Star Rating */}
            <div>
              <label className="block text-sm text-slate-400 mb-3">评分</label>
              <div className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <StarRating rating={rating} onChange={(r) => setRating(r as 1 | 2 | 3 | 4 | 5)} />
                <span className="text-sm text-slate-400">
                  {rating === 5 ? '非常满意' :
                   rating === 4 ? '满意' :
                   rating === 3 ? '一般' :
                   rating === 2 ? '不满意' : '非常不满意'}
                </span>
              </div>
            </div>

            {/* Detailed Comment */}
            <div>
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors mb-2"
              >
                {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                {showDetails ? '收起详细反馈' : '添加详细反馈'}
              </button>

              {showDetails && (
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="请详细描述您的建议或问题..."
                  className="w-full h-32 px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-300 placeholder-slate-500 focus:outline-none focus:border-cyan-500 resize-none"
                />
              )}
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      {!submitted && (
        <div className="p-4 border-t border-slate-700/50">
          <button
            onClick={handleSubmit}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-xl hover:opacity-90 transition-opacity"
          >
            <Send className="w-5 h-5" />
            <span className="font-medium">提交反馈</span>
          </button>
        </div>
      )}
    </div>
  );
};

// ==================== Floating Feedback Button ====================

export const FeedbackFloatingButton: React.FC<{ onClick: () => void }> = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="fixed right-4 bottom-20 w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 text-white shadow-lg flex items-center justify-center hover:scale-110 transition-transform z-40"
    >
      <MessageSquare className="w-5 h-5" />
    </button>
  );
};

export default FeedbackPanel;
