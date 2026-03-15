# AI-SecOps项目Langflow SOAR 集成与 Harness Engineering 规格书

## 0. 架构准则与 AI 约束 (Architectural Constraints for Claude Code)

🤖 **Claude Code 提示 (System Prompt for Claude Code):**
> "在执行本指南中的任何编码任务时，你必须遵守以下底线：
> 1. **零运行时依赖**：Langflow 服务仅在**设计态 (Design Time)** 运行，导出 JSON。后端的 L6 (`layer6_orchestrator`) 必须在**完全没有 Langflow 运行时依赖**的情况下，将 JSON 编译为原生的 `langgraph.graph.StateGraph` 并执行。
> 2. **状态纯洁性**：所有图节点的数据传递必须严格符合 `models.IncidentState` Pydantic 模型，禁止使用无类型的 `dict` 或 `**kwargs`。
> 3. **强制隔离**：Langflow 生成的任何节点代码，只能调用 `layer1` 到 `layer8` 暴露的内部函数，**绝对禁止**在节点脚本中直接写死 SQL 查询或发起未经鉴权的外部 HTTP 请求。
> 4. **无缝注入 `trace_id`**：图执行的整个生命周期必须在 `IncidentState` 中携带 `trace_id`，用于触发后续的 WebSocket HITL 事件。"

---

## 第一部分：后端引擎面集成 (L6 Orchestrator & LangGraph)

### 1.1 核心解析器开发：从 JSON 到 StateGraph
这是整个集成的核心。我们需要编写一个解析器，将前端传来的 Langflow JSON 拓扑转换为 LangGraph 原生代码，并**动态注入人机协同 (HITL) 断点**。

**文件路径**: `backend/src/data_plane/layer6_orchestrator/langflow_parser.py`

**🤖 Claude Code 开发指令：**
1. 定义 `LangflowNode` 和 `LangflowEdge` 的 Pydantic 模型，用于校验解析前端传来的剧本 JSON。
2. 开发 `build_graph_from_langflow(flow_json: dict) -> StateGraph` 函数。
3. **架构约束实现**：在解析节点时，如果检测到该节点的 `type` 包含关键字 `Action_` 或 `OpenC2_`，必须将其 ID 自动加入到 `interrupt_before` 列表中。

**参考代码桩 (Code Skeleton)：**
```python
from langgraph.graph import StateGraph, END
from typing import List, Dict, Callable
from backend.src.models import IncidentState
from backend.src.data_plane.layer6_orchestrator.registry import NODE_REGISTRY

def build_graph_from_langflow(flow_json: dict) -> StateGraph:
    """
    将 Langflow 导出的 DAG JSON 编译为可持久化、带 HITL 的 LangGraph 状态机。
    """
    workflow = StateGraph(IncidentState)
    high_risk_nodes: List[str] = []
    
    # 1. 注册节点
    for node in flow_json.get("nodes",[]):
        node_id = node["id"]
        node_type = node.get("data", {}).get("type")
        
        # 严格防御：未注册的黑客节点禁止加载
        if node_type not in NODE_REGISTRY:
            raise ValueError(f"Harness Error: Unauthorized node type '{node_type}'")
            
        workflow.add_node(node_id, NODE_REGISTRY[node_type])
        
        # 拦截层设计：所有 L8 执行节点自动强制挂起 (HITL)
        if node_type.startswith("OpenC2_") or "Block" in node_type:
            high_risk_nodes.append(node_id)
            
    # 2. 编排边 (Edges)
    for edge in flow_json.get("edges", []):
        workflow.add_edge(edge["source"], edge["target"])
        
    # TODO: Claude Code 需补充 add_conditional_edges 的逻辑映射
        
    # 3. 编译图，注入 Postgres 持久化内存 (Checkpointer)
    from langgraph.checkpoint.postgres import PostgresSaver
    # 注意：在测试环境下应使用 MemorySaver()
    
    return workflow.compile(
        checkpointer=PostgresSaver(), # 使用项目中已有的 PG 连接池
        interrupt_before=high_risk_nodes
    )
```

### 1.2 节点注册表开发 (Component Registry)
为了避免 Langflow 中出现任意代码执行 (RCE) 漏洞，必须开发一个本地节点注册表。Langflow 中拖拽的节点只是一个“空壳标识符”，真正的 Python 逻辑在我们的后端代码里。

**文件路径**: `backend/src/data_plane/layer6_orchestrator/registry.py`

**🤖 Claude Code 开发指令：**
1. 创建一个字典 `NODE_REGISTRY: Dict[str, Callable[[IncidentState], dict]]`。
2. 实现至少三个标准节点函数：
   - `OCSF_Normalizer_Node`：调用 `layer2_normalizer`。
   - `AI_Triage_Node`：调用 `layer5_analyzer`。
   - `OpenC2_Isolate_Node`：调用 `layer8_executor` 生成隔离指令。

---

## 第二部分：前端控制面集成 (BFF & UI)

### 2.1 Iframe 容器与 JWT SSO
我们需要在 React 中安全地嵌入 Langflow 的界面，同时保证不需要二次登录，并传递当前的明暗/战时主题。

**文件路径**: `frontend/src/pages/Settings/PlaybookEditor.tsx`

**🤖 Claude Code 开发指令：**
1. 开发 `PlaybookEditor` 组件，使用 `iframe` 嵌入。
2. 从 `useAppStore` 提取 JWT token 和 `warMode` 状态。
3. 使用 `window.postMessage` 监听 Langflow 中发出的“保存”事件，拦截其 JSON 数据并转交给您的 FastAPI 后端 `/api/v1/orchestrator/playbooks` 接口保存，**不要让 Langflow 自己存入它的 SQLite**。

**参考代码桩 (Code Skeleton)：**
```tsx
import React, { useEffect, useRef } from 'react';
import { useAppStore } from '@/stores/useAppStore';

export const PlaybookEditor: React.FC = () => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const token = useAppStore(state => state.auth.token);
  const warMode = useAppStore(state => state.warMode);
  
  // 主题与鉴权注入
  const langflowUrl = `${import.meta.env.VITE_LANGFLOW_URL}/?token=${token}&theme=${warMode ? 'dark-war' : 'dark-cyber'}`;

  useEffect(() => {
    // Harness: 监听 Langflow iframe 发来的 Save 动作，接管 JSON 存储
    const handleMessage = async (event: MessageEvent) => {
      if (event.data?.type === 'LANGFLOW_SAVE_FLOW') {
        const flowJson = event.data.payload;
        // 将设计态的 JSON 送回 AI-SecOps 后端保存
        await fetch('/api/v1/orchestrator/playbooks', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ flow_data: flowJson })
        });
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [token]);

  return (
    <div className={`w-full h-[80vh] rounded-xl border ${warMode ? 'border-red-900' : 'border-slate-700'}`}>
      <iframe 
        ref={iframeRef}
        src={langflowUrl} 
        className="w-full h-full border-none"
        title="SOAR Visual Editor"
      />
    </div>
  );
};
```

---

## 第三部分：Harness Engineering 质量保证 (Testing & Linting)

这部分对于指导 AI 编写出**健壮的工业级代码**至关重要。

### 3.1 架构约束检查器 (Ruff Rules / Pytest Architecture Test)
必须防止开发人员（或 AI）在后续维护中破坏层级隔离。

**文件路径**: `backend/tests/architecture/test_layer_isolation.py`

**🤖 Claude Code 开发指令：**
1. 编写一个测试，分析 AST 或导入路径。
2. 断言 `layer1` 到 `layer5` 绝对不能导入 `layer6` (Orchestrator) 或 `layer8` (Executor)。
3. 断言 `layer6_orchestrator` 下的剧本节点，只能通过注册表进行相互调用。

### 3.2 确定性断言：HITL 中断行为测试 (Deterministic HITL Mock)
测试 LangGraph 是否按照我们的要求在危险节点前**精确地挂起**，这是 SOAR 系统的生命线。

**文件路径**: `backend/tests/layer6_orchestrator/test_langgraph_hitl.py`

**🤖 Claude Code 开发指令：**
1. 使用一个预制的 Langflow JSON（包含 `extract_ioc` -> `ai_triage` -> `OpenC2_Block_IP` 的微型剧本）。
2. 调用 `build_graph_from_langflow` 并在 `MemorySaver` 模式下编译图。
3. 提供一份模拟的 `IncidentState` (trace_id: "test-hitl-001", victim_ip: "10.0.0.5")。
4. **核心断言**：运行 `.invoke()`，断言图执行在到达 `OpenC2_Block_IP` 节点时停止。
5. **恢复断言**：使用 `.update_state()` 模拟前端传来的审批通过指令，再次运行，断言图成功流转到 `END` 并正确生成了 OpenC2 JSON 载荷。

**测试代码示例 (引导 AI 的范式)：**
```python
import pytest
from langgraph.checkpoint.memory import MemorySaver
from backend.src.data_plane.layer6_orchestrator.langflow_parser import build_graph_from_langflow

def test_critical_path_triggers_human_approval(mock_playbook_json):
    """
    Harness Deterministic Test: 确保高危动作必定触发中断
    """
    # 1. 编译图 (带内存 Checkpointer)
    graph = build_graph_from_langflow(mock_playbook_json)
    
    # 2. 初始化状态与线程上下文
    initial_state = {"trace_id": "trk-123", "target_ip": "1.1.1.1", "action_approved": False}
    thread_config = {"configurable": {"thread_id": "test_thread_1"}}
    
    # 3. 运行图
    for event in graph.stream(initial_state, config=thread_config):
        pass # 消费事件流
        
    # 4. Harness 断言 1：图必须挂起在下一个节点是 OpenC2 执行节点的状态
    snapshot = graph.get_state(thread_config)
    assert snapshot.next[0] == "OpenC2_Block_IP", "Harness Failure: 图未在高危节点前挂起"
    
    # 5. 模拟人类在环 (HITL) 批准
    graph.update_state(thread_config, {"action_approved": True}, as_node="human_approval")
    
    # 6. 恢复执行
    for event in graph.stream(None, config=thread_config):
        pass
        
    # 7. Harness 断言 2：图必须执行完毕
    final_snapshot = graph.get_state(thread_config)
    assert not final_snapshot.next, "Harness Failure: 批准后图未能继续执行完毕"
```

### 3.3 CI/CD 流水线指令 (GitHub Actions / GitLab CI)
在 `pyproject.toml` 中配置 `datamodel-code-generator` 工具，在每次后端 Pydantic 模型（特别是 `IncidentState` 和 `ApprovalTask`）发生变更时，自动生成对应的前端 TypeScript 接口。这是实现单一真相源 (SSOT) 的核心。

---

## 第四部分：交由 Claude Code 执行的启动指令

将以上内容作为上下文提交给 Claude Code 后，通过以下组合指令驱动其开始工作：

> **👨‍💻 User to Claude Code:**
> "Claude，我已经提供了《AI-SecOps 前后端详细设计文档》以及《Langflow SOAR 集成与 Harness Engineering 规格书》。
>
> 现在开始执行**第一阶段任务**：
> 请在 `backend/src/data_plane/layer6_orchestrator/` 目录下创建 `langflow_parser.py` 和 `registry.py`。
> 要求：
> 1. 严格按照规格书中的 `build_graph_from_langflow` 逻辑实现。
> 2. Pydantic 状态类 `IncidentState` 必须包含 `trace_id`。
> 3. 写完后，立刻在 `backend/tests/layer6_orchestrator/` 目录下创建对应的断言测试 `test_langgraph_hitl.py`。
> 4. 使用 `pytest` 运行该测试，修复所有错误，直到测试变绿。
>
> 随时汇报你的进度，在生成外部 API 调用时请使用 mock。"