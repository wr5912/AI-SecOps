/**
 * PlaybookEditor - Langflow SOAR 可视化编排编辑器
 * 
 * 功能：
 * - iframe 嵌入 Langflow 编辑器
 * - JWT token 认证透传
 * - warMode 主题透传
 * - postMessage 监听保存事件，接管 JSON 存储到 AI-SecOps 后端
 */

import React, { useEffect, useRef, useState } from 'react';
import { useAppStore } from '../../stores/useAppStore';

interface PlaybookEditorProps {
  /** 剧本ID，如果是新剧本则为 undefined */
  playbookId?: string;
  /** 关闭编辑器的回调 */
  onClose?: () => void;
}

export const PlaybookEditor: React.FC<PlaybookEditorProps> = ({
  playbookId,
  onClose,
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // 从 Zustand store 获取认证和主题状态
  const token = useAppStore((state: any) => state.auth?.token);
  const warMode = useAppStore((state: any) => state.warMode);
  const addNotification = useAppStore((state: any) => state.addNotification);
  
  // 构建 Langflow URL
  const langflowUrl = React.useMemo(() => {
    const baseUrl = (import.meta as any).env?.VITE_LANGFLOW_URL || 'http://localhost:7860';
    
    // 如果是编辑现有剧本，使用 /flow/{id} 路由
    if (playbookId) {
      return `${baseUrl}/flow/${playbookId}`;
    }
    
    // 新建剧本使用 /flows 路由
    return `${baseUrl}/flows`;
  }, [playbookId]);

  // 监听 Langflow iframe 发来的消息
  useEffect(() => {
    const handleMessage = async (event: MessageEvent) => {
      // 安全检查：验证消息来源
      // 在生产环境中应该验证 event.origin
      
      const { data } = event;
      
      // 处理 Langflow 保存事件
      if (data?.type === 'LANGFLOW_SAVE_FLOW') {
        const flowJson = data.payload;
        
        console.log('[PlaybookEditor] Received flow save event:', flowJson);
        
        try {
          // 将设计态的 JSON 送回 AI-SecOps 后端保存
          const response = await fetch('/api/v1/orchestrator/playbooks', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': token ? `Bearer ${token}` : '',
            },
            body: JSON.stringify({
              flow_data: flowJson,
              playbook_id: playbookId,
              name: flowJson.name || 'Untitled Playbook',
              description: flowJson.description || '',
            }),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to save playbook: ${response.statusText}`);
          }
          
          const result = await response.json();
          
          // 通知用户保存成功
          addNotification({
            type: 'success',
            message: `剧本 "${flowJson.name || 'Untitled'}" 保存成功`,
          });
          
          console.log('[PlaybookEditor] Playbook saved:', result);
          
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : 'Unknown error';
          console.error('[PlaybookEditor] Save failed:', errorMessage);
          
          setError(`保存失败: ${errorMessage}`);
          
          addNotification({
            type: 'error',
            message: `剧本保存失败: ${errorMessage}`,
          });
        }
      }
      
      // 处理 Langflow 加载完成事件
      if (data?.type === 'LANGFLOW_FLOW_LOADED') {
        console.log('[PlaybookEditor] Flow loaded:', data.payload);
        setIsLoading(false);
      }
      
      // 处理错误事件
      if (data?.type === 'LANGFLOW_ERROR') {
        console.error('[PlaybookEditor] Langflow error:', data.payload);
        setError(data.payload?.message || 'Unknown error');
      }
    };
    
    window.addEventListener('message', handleMessage);
    
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, [token, playbookId, addNotification]);

  // 加载超时处理
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (isLoading) {
        setIsLoading(false);
      }
    }, 10000); // 10秒超时
    
    return () => clearTimeout(timeout);
  }, [isLoading]);

  // 主题样式
  const loadingClass = warMode
    ? 'text-red-400'
    : 'text-blue-400';

  return (
    <div className="flex flex-col h-full">
      {/* 头部工具栏 */}
      <div className={`
        flex items-center justify-between px-4 py-2 
        ${warMode 
          ? 'bg-red-950/50 border-b border-red-900/50' 
          : 'bg-slate-800/50 border-b border-slate-700'}
      `}>
        <div className="flex items-center gap-4">
          <h3 className={`
            text-lg font-semibold
            ${warMode ? 'text-red-100' : 'text-slate-100'}
          `}>
            SOAR 剧本编辑器
          </h3>
          {playbookId && (
            <span className={`
              text-sm px-2 py-0.5 rounded
              ${warMode 
                ? 'bg-red-900/30 text-red-400' 
                : 'bg-slate-700 text-slate-400'}
            `}>
              编辑模式
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              // 向 iframe 发送保存指令
              iframeRef.current?.contentWindow?.postMessage(
                { type: 'REQUEST_SAVE_FLOW' },
                '*'
              );
            }}
            className={`
              px-3 py-1.5 text-sm font-medium rounded transition-colors
              ${warMode
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'}
            `}
          >
            保存剧本
          </button>
          
          {onClose && (
            <button
              onClick={onClose}
              className={`
                px-3 py-1.5 text-sm font-medium rounded transition-colors
                ${warMode
                  ? 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                  : 'bg-slate-700 hover:bg-slate-600 text-slate-300'}
              `}
            >
              关闭
            </button>
          )}
        </div>
      </div>
      
      {/* 错误提示 */}
      {error && (
        <div className={`
          px-4 py-2 text-sm
          ${warMode 
            ? 'bg-red-900/30 text-red-400 border-b border-red-900/50' 
            : 'bg-red-900/20 text-red-400 border-b border-red-800/30'}
        `}>
          {error}
          <button 
            onClick={() => setError(null)}
            className="ml-2 underline hover:no-underline"
          >
            关闭
          </button>
        </div>
      )}
      
      {/* 编辑器容器 */}
      <div className="flex-1 relative">
        {/* 加载状态 */}
        {isLoading && (
          <div className={`
            absolute inset-0 flex items-center justify-center z-10
            ${warMode ? 'bg-slate-950' : 'bg-slate-900'}
          `}>
            <div className="flex flex-col items-center gap-3">
              <div className={`
                w-8 h-8 border-2 border-t-transparent rounded-full animate-spin
                ${loadingClass}
              `} />
              <span className={loadingClass}>
                加载 Langflow 编辑器...
              </span>
            </div>
          </div>
        )}
        
        {/* Langflow iframe */}
        <iframe
          ref={iframeRef}
          src={langflowUrl}
          className="w-full h-full border-none"
          title="SOAR Visual Editor"
          allow="clipboard-read; clipboard-write"
          sandbox="allow-scripts allow-same-origin allow-forms"
        />
      </div>
      
      {/* 底部状态栏 */}
      <div className={`
        px-4 py-1.5 text-xs flex items-center justify-between
        ${warMode 
          ? 'bg-red-950/30 border-t border-red-900/30 text-red-500' 
          : 'bg-slate-800/30 border-t border-slate-700 text-slate-500'}
      `}>
        <span>
          Langflow 可视化编排 | {warMode ? '战时模式' : '普通模式'}
        </span>
        <span>
          {token ? '已登录' : '未认证'}
        </span>
      </div>
    </div>
  );
};

/**
 * 独立的剧本编辑器页面组件
 * 用于全屏展示剧本编辑器
 */
export const PlaybookEditorPage: React.FC = () => {
  const warMode = useAppStore((state: any) => state.warMode);
  
  return (
    <div className={`
      h-screen flex flex-col
      ${warMode ? 'bg-slate-950' : 'bg-slate-900'}
    `}>
      <PlaybookEditor 
        onClose={() => window.history.back()}
      />
    </div>
  );
};

export default PlaybookEditor;
