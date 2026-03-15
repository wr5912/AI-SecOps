/**
 * AISecOps - Global State Management with Zustand
 * Following FRONTEND_DESIGN_DOCUMENT.md Chapter 10.1
 */
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

// ==================== Type Definitions ====================

// Following FRONTEND_DESIGN_DOCUMENT.md Chapter 4 Data Models
// snake_case for API compatibility, camelCase for internal use with proper mapping

export type AssetStatus = 'normal' | 'warning' | 'critical' | 'compromised';
export type AssetType = 'server' | 'endpoint' | 'database' | 'firewall' | 'iot' | 'cloud';
export type AlertLevel = 'critical' | 'high' | 'medium' | 'low';
export type StorylineStatus = 'active' | 'investigating' | 'contained' | 'resolved';
export type UserRole = 'admin' | 'analyst' | 'viewer' | 'ciso';
export type ApprovalStatus = 'pending' | 'approved' | 'rejected';

// Asset Interface - Aligned with Design Document Section 4.1
export interface Asset {
  id: string;
  trace_id: string;  // Required per design document
  name: string;
  ip: string;
  type: AssetType;
  status: AssetStatus;
  risk_score: number;  // Changed from 'risk' to match design
  os: string;
  department: string;
  owner: string;
  ports: number[];
  vulnerabilities: { cvss: number; name: string }[];
  connections: string[];
  lastSeen: string;
}

// Alert Interface - Aligned with Design Document Section 4.2
export interface Alert {
  id: string;
  trace_id: string;  // Required per design document
  severity: AlertLevel;  // Changed from 'level' to match design
  attacker_ip: string;  // Changed from 'source' to match design
  victim_ip: string;  // Changed from 'target' to match design
  type: string;
  time: string;
  mitre_tactic: string;  // Changed from 'mitreTactic' to match design (snake_case)
  confidence_score: number;  // Changed from 'confidence' to match design
  storyline_id?: string;  // Changed from 'storylineId' to match design
  acknowledged: boolean;
}

// Legacy aliases for backward compatibility during migration
export type AlertLegacy = Alert & {
  level?: AlertLevel;
  source?: string;
  target?: string;
  mitreTactic?: string;
  confidence?: number;
  storylineId?: string;
};

// Storyline Interface - Aligned with Design Document Section 4.3
export interface Storyline {
  id: string;
  trace_id: string;  // Required per design document
  title: string;
  description: string;
  severity: AlertLevel;
  confidence_score: number;  // Changed from 'confidence' to match design
  assets: string[];
  mitre_tactics: string[];  // Changed from 'mitreTactics' to match design (snake_case)
  steps: { time: string; event: string; node: string }[];
  status: StorylineStatus;
  aiReasoning?: string[];
}

// Chat Message Interface - Aligned with Design Document Section 4.4
export interface ChatMessage {
  id: string;
  trace_id: string;  // Required per design document
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  actions?: { label: string; action: string }[];
}

// HITL Approval Request
export interface ApprovalRequest {
  id: string;
  type: 'isolation' | 'block_ip' | 'quarantine' | 'script_execution';
  target: string;
  description: string;
  requester: string;
  requestTime: string;
  status: ApprovalStatus;
  approver?: string;
  approveTime?: string;
  traceId?: string;
  priority: AlertLevel;
}

// User Session
export interface UserSession {
  id: string;
  name: string;
  role: UserRole;
  avatar?: string;
  permissions: string[];
}

// Feedback Action Types
export type FeedbackActionType =
  | 'THUMBS_UP'
  | 'THUMBS_DOWN'
  | 'FALSE_POSITIVE'
  | 'TRUE_POSITIVE'
  | 'AI_CORRECT'
  | 'AI_INCORRECT';

// Feedback Target Types
export type FeedbackTargetType = 'ALERT' | 'STORYLINE' | 'DISPOSAL_RECOMMENDATION';

// Feedback Entry
export interface FeedbackEntry {
  id: string;
  type: FeedbackTargetType;
  action: FeedbackActionType;
  targetId: string;
  rating?: 1 | 2 | 3 | 4 | 5;
  comment?: string;
  timestamp: string;
  traceId?: string;
  userId?: string;
}

// Quick Feedback State (for optimistic UI updates)
export interface QuickFeedbackState {
  [targetId: string]: FeedbackActionType;
}

// ==================== App State Interface ====================

export interface AppState {
  // War Mode
  warMode: boolean;
  toggleWarMode: () => void;

  // Assets
  assets: Record<string, Asset>;
  setAssets: (assets: Asset[]) => void;
  updateAsset: (id: string, updates: Partial<Asset>) => void;
  selectAsset: (id: string | null) => void;
  selectedAssetId: string | null;

  // Alerts
  alerts: Alert[];
  setAlerts: (alerts: Alert[]) => void;
  addAlert: (alert: Alert) => void;
  acknowledgeAlert: (id: string) => void;

  // Storylines
  storylines: Storyline[];
  setStorylines: (storylines: Storyline[]) => void;
  selectStoryline: (id: string | null) => void;
  selectedStorylineId: string | null;
  updateStorylineStatus: (id: string, status: StorylineStatus) => void;

  // AI Copilot
  copilotOpen: boolean;
  toggleCopilot: () => void;
  copilotMessages: ChatMessage[];
  addCopilotMessage: (message: ChatMessage) => void;
  clearCopilotMessages: () => void;
  currentContext: string | null;
  setCurrentContext: (context: string | null) => void;

  // HITL Approvals
  pendingApprovals: ApprovalRequest[];
  addApprovalRequest: (request: ApprovalRequest) => void;
  approveRequest: (id: string, approver: string) => void;
  rejectRequest: (id: string, approver: string) => void;

  // Feedback
  feedbackEntries: FeedbackEntry[];
  quickFeedback: QuickFeedbackState;
  addFeedback: (feedback: FeedbackEntry) => void;
  setQuickFeedback: (targetId: string, action: FeedbackActionType) => void;
  removeQuickFeedback: (targetId: string) => void;

  // User & RBAC
  currentUser: UserSession | null;
  setCurrentUser: (user: UserSession | null) => void;
  hasPermission: (permission: string) => boolean;

  // UI State
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;

  // WebSocket Status
  wsConnected: boolean;
  setWsConnected: (connected: boolean) => void;

  // Notifications
  notifications: { id: string; message: string; type: 'info' | 'warning' | 'error' | 'success'; timestamp: Date }[];
  addNotification: (notification: Omit<AppState['notifications'][0], 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;

  // Trace ID for distributed tracing
  currentTraceId: string | null;
  setCurrentTraceId: (traceId: string | null) => void;

  // Computed helpers
  getSelectedAsset: () => Asset | null;
  getSelectedStoryline: () => Storyline | null;
  getAssetById: (id: string) => Asset | undefined;
  getAlertsByAsset: (assetId: string) => Alert[];
  getStorylinesByAsset: (assetId: string) => Storyline[];
  getThreatLevel: () => number;
}

// ==================== Zustand Store ====================

export const useAppStore = create<AppState>()(
  subscribeWithSelector((set, get) => ({
    // War Mode
    warMode: false,
    toggleWarMode: () => set((state) => ({ warMode: !state.warMode })),

    // Assets
    assets: {},
    setAssets: (assets) => set((state) => {
      const assetMap: Record<string, Asset> = {};
      assets.forEach((asset) => {
        assetMap[asset.id] = asset;
      });
      return { assets: assetMap };
    }),
    updateAsset: (id, updates) => set((state) => ({
      assets: {
        ...state.assets,
        [id]: { ...state.assets[id], ...updates },
      },
    })),
    selectAsset: (id) => set({ selectedAssetId: id }),
    selectedAssetId: null,

    // Alerts
    alerts: [],
    setAlerts: (alerts) => set({ alerts }),
    addAlert: (alert) => set((state) => ({ alerts: [alert, ...state.alerts] })),
    acknowledgeAlert: (id) => set((state) => ({
      alerts: state.alerts.map((a) =>
        a.id === id ? { ...a, acknowledged: true } : a
      ),
    })),

    // Storylines
    storylines: [],
    setStorylines: (storylines) => set({ storylines }),
    selectStoryline: (id) => set({ selectedStorylineId: id }),
    selectedStorylineId: null,
    updateStorylineStatus: (id, status) => set((state) => ({
      storylines: state.storylines.map((s) =>
        s.id === id ? { ...s, status } : s
      ),
    })),

    // AI Copilot
    copilotOpen: false,
    toggleCopilot: () => set((state) => ({ copilotOpen: !state.copilotOpen })),
    copilotMessages: [],
    addCopilotMessage: (message) => set((state) => ({
      copilotMessages: [...state.copilotMessages, message],
    })),
    clearCopilotMessages: () => set({ copilotMessages: [] }),
    currentContext: null,
    setCurrentContext: (context) => set({ currentContext: context }),

    // HITL Approvals
    pendingApprovals: [],
    addApprovalRequest: (request) => set((state) => ({
      pendingApprovals: [...state.pendingApprovals, request],
    })),
    approveRequest: (id, approver) => set((state) => ({
      pendingApprovals: state.pendingApprovals.map((r) =>
        r.id === id ? { ...r, status: 'approved' as ApprovalStatus, approver, approveTime: new Date().toISOString() } : r
      ),
    })),
    rejectRequest: (id, approver) => set((state) => ({
      pendingApprovals: state.pendingApprovals.map((r) =>
        r.id === id ? { ...r, status: 'rejected' as ApprovalStatus, approver, approveTime: new Date().toISOString() } : r
      ),
    })),

    // Feedback
    feedbackEntries: [],
    quickFeedback: {},
    addFeedback: (feedback) => set((state) => ({
      feedbackEntries: [...state.feedbackEntries, feedback],
    })),
    setQuickFeedback: (targetId, action) => set((state) => ({
      quickFeedback: { ...state.quickFeedback, [targetId]: action },
    })),
    removeQuickFeedback: (targetId) => set((state) => {
      const newQuickFeedback = { ...state.quickFeedback };
      delete newQuickFeedback[targetId];
      return { quickFeedback: newQuickFeedback };
    }),

    // User & RBAC
    currentUser: null,
    setCurrentUser: (user) => set({ currentUser: user }),
    hasPermission: (permission) => {
      const { currentUser } = get();
      if (!currentUser) return false;
      return currentUser.permissions.includes(permission) || currentUser.role === 'admin';
    },

    // UI State
    sidebarCollapsed: false,
    toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    theme: 'dark',
    setTheme: (theme) => set({ theme }),

    // WebSocket
    wsConnected: false,
    setWsConnected: (connected) => set({ wsConnected: connected }),

    // Notifications
    notifications: [],
    addNotification: (notification) => set((state) => ({
      notifications: [
        ...state.notifications,
        { ...notification, id: `notif-${Date.now()}`, timestamp: new Date() },
      ],
    })),
    removeNotification: (id) => set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),

    // Trace ID
    currentTraceId: null,
    setCurrentTraceId: (traceId) => set({ currentTraceId: traceId }),

    // Computed Helpers
    getSelectedAsset: () => {
      const { assets, selectedAssetId } = get();
      return selectedAssetId ? assets[selectedAssetId] || null : null;
    },
    getSelectedStoryline: () => {
      const { storylines, selectedStorylineId } = get();
      return storylines.find((s) => s.id === selectedStorylineId) || null;
    },
    getAssetById: (id) => {
      const { assets } = get();
      return assets[id];
    },
    getAlertsByAsset: (assetId) => {
      const { alerts } = get();
      return alerts.filter((a) => a.source === assetId || a.target === assetId);
    },
    getStorylinesByAsset: (assetId) => {
      const { storylines } = get();
      return storylines.filter((s) => s.assets.includes(assetId));
    },
    getThreatLevel: () => {
      const { assets, warMode } = get();
      if (warMode) return 92;
      const compromised = Object.values(assets).filter((a) => a.status === 'compromised' || a.status === 'critical').length;
      const total = Object.keys(assets).length || 1;
      return Math.min(100, Math.round((compromised / total) * 100) + 30);
    },
  }))
);

// ==================== Selectors (Performance Optimization) ====================

// Memoized selectors for frequently accessed data
export const selectWarMode = (state: AppState) => state.warMode;
export const selectAssets = (state: AppState) => Object.values(state.assets);
export const selectAlerts = (state: AppState) => state.alerts;
export const selectStorylines = (state: AppState) => state.storylines;
export const selectPendingApprovals = (state: AppState) => state.pendingApprovals;
export const selectWsConnected = (state: AppState) => state.wsConnected;
export const selectCurrentUser = (state: AppState) => state.currentUser;
export const selectNotifications = (state: AppState) => state.notifications;

// Derived selectors
export const selectCriticalAssets = (state: AppState) =>
  Object.values(state.assets).filter((a) => a.status === 'critical' || a.status === 'compromised');

export const selectUnacknowledgedAlerts = (state: AppState) =>
  state.alerts.filter((a) => !a.acknowledged);

export const selectActiveStorylines = (state: AppState) =>
  state.storylines.filter((s) => s.status === 'active');

export const selectPendingApprovalCount = (state: AppState) =>
  state.pendingApprovals.filter((a) => a.status === 'pending').length;

export default useAppStore;
