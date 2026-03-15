# AI-SecOps 项目核心配置

## 项目概述

**项目名称**: AI-SecOps 企业智能安全运营平台  
**版本**: v1.0.0  
**架构**: 九层技术架构 + 三层能力架构  
**开发模式**: Harness Engineering + AI Vibe Coding

---

## 一、项目架构

### 1.1 三层能力架构

| 层级 | 名称 | 核心能力 |
|------|------|----------|
| 后台 | Security Intelligence Layer | 实时威胁分析、自动响应、协同联防 |
| 前台 | Security Operations Interface | 自然语言交互、动态可视化、人机协同 |
| 反馈层 | Continuous Improvement Engine | 运营反馈、模型优化、知识沉淀 |

### 1.2 九层技术架构

| 层级 | 名称 | 技术栈 | 核心功能 |
|------|------|--------|----------|
| L1 | 防洪网关层 | FastAPI + Aho-Corasick | Sigma规则预过滤、高性能日志接收 |
| L2 | 数据清洗层 | DSPy + Pydantic | OCSF标准化、DSPy实体提取 |
| L3 | 知识图谱层 | Neo4j | STIX 2.1图谱构建、攻击链路发现 |
| L4 | 信息压缩层 | DSPy | 时序聚合、告警故事线生成 |
| L5 | 智能分析层 | DSPy + LangChain | MITRE ATT&CK映射、威胁研判 |
| L6 | 控制编排层 | LangGraph | SOAR剧本、HITL审批流 |
| L7 | 对抗推演层 | AutoGen | 红蓝对抗、攻击路径预测 |
| L8 | 终端执行层 | OpenC2 | pi-mono Agent、标准化指令 |
| L9 | 复盘研报层 | CrewAI | 自动报告、合规归档 |

---

## 二、技术栈选型

### 2.1 后端技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| API框架 | FastAPI | ^0.109.0 |
| 异步ORM | SQLAlchemy 2.0 + asyncpg | ^2.0.0 |
| 图数据库 | Neo4j Driver | ^5.0.0 |
| 消息队列 | Redis (aioredis) | ^2.0.0 |
| AI框架 | DSPy | ^2.5.0 |
| 编排框架 | LangGraph | ^0.1.0 |
| 多Agent | AutoGen | ^0.2.0 |
| 日志处理 | pyahocorasick | ^1.4.0 |
| JSON处理 | orjson | ^3.9.0 |
| LLM适配 | OpenAI SDK | ^1.0.0 |

### 2.2 前端技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | React | ^18.2.0 |
| 语言 | TypeScript | ^5.3.0 |
| 构建工具 | Vite | ^5.0.0 |
| 样式 | Tailwind CSS | ^3.3.0 |
| 拓扑图 | @xyflow/react | ^12.0.0 |
| 状态管理 | Zustand | ^4.4.0 |
| 图表 | Recharts | ^2.10.0 |
| 实时通信 | socket.io-client | ^4.7.0 |
| HTTP客户端 | Axios | ^1.6.0 |

### 2.3 LLM配置

#### 开发环境 (互联网)
```bash
# Kimi
LLM_PROVIDER=kimi
KIMI_API_KEY=sk-xxx
KIMI_MODEL_NAME=kimi-k2.5

# MiniMax
LLM_PROVIDER=minimax
MINIMAX_API_KEY=xxx
MINIMAX_MODEL_NAME=minimax-m2.5
```

#### 部署环境 (离线)
```bash
# vLLM 本地模型
LLM_PROVIDER=vllm
VLLM_BASE_URL=http://localhost:8000/v1
LLM_MODEL_NAME=Qwen/Qwen2.5-14B-Instruct

# Ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=deepseek-r1:14b
```

---

## 三、数据标准

### 3.1 OCSF (Open Cybersecurity Schema Framework)
- 参考: https://schema.ocsf.io
- 用于: 日志标准化格式

### 3.2 STIX 2.1 (Structured Threat Information Expression)
- 参考: https://docs.oasis-open.org/cti/stix/v2.1/
- 用于: 威胁情报图谱建模

### 3.3 MITRE ATT&CK
- 参考: https://attack.mitre.org/
- 用于: 战术技术映射

### 3.4 OpenC2 (Open Command and Control)
- 参考: https://openc2.org/
- 用于: 自动化响应指令

### 3.5 Sigma规则
- 参考: https://github.com/SigmaHQ/sigma
- 用于: 告警检测规则

---

## 四、API接口规范

### 4.1 RESTful API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/topology/graph | 获取网络拓扑 |
| GET | /api/v1/assets/{id}/hologram | 获取资产详情 |
| POST | /api/v1/assets/{id}/actions | 执行资产操作 |
| GET | /api/v1/incidents | 获取告警列表 |
| GET | /api/v1/incidents/{trace_id} | 获取告警详情 |
| GET | /api/v1/storylines | 获取故事线列表 |
| GET | /api/v1/orchestration/pending | 获取待审批任务 |
| POST | /api/v1/orchestration/{trace_id}/approve | 审批通过 |
| POST | /api/v1/orchestration/{trace_id}/reject | 审批拒绝 |
| POST | /api/v1/feedback/submit | 提交反馈 |
| GET | /api/v1/copilot/chat/stream | AI Copilot对话(SSE) |

### 4.2 WebSocket消息

| 消息类型 | 说明 |
|----------|------|
| ASSET_STATUS_UPDATE | 资产状态更新 |
| HITL_APPROVAL_REQUIRED | 审批请求 |
| NEW_ALERT | 新告警通知 |
| ANALYSIS_STAGE_CHANGED | AI分析进度 |
| WAR_MODE_TRIGGERED | 战时模式触发 |
| NEW_STORYLINE | 新故事线生成 |

---

## 五、编码约定

### 5.1 Python后端

```python
# 1. 异步优先 - 所有IO操作必须使用async/await
async def fetch_data():
    async with async_session() as session:
        result = await session.execute(select(Model))
        return result.scalars().all()

# 2. Pydantic模型 - 所有API输入输出必须使用Pydantic
class IncidentResponse(BaseModel):
    trace_id: str
    severity: AlertSeverity
    attacker_ip: str | None = None

# 3. 必填trace_id - 所有核心实体必须包含trace_id
class CoreEntity(BaseModel):
    trace_id: str  # 贯穿全程的追踪ID
```

### 5.2 TypeScript前端

```typescript
// 1. 严格类型 - 禁止使用any
interface Alert {
  trace_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
}

// 2. 组件命名 - PascalCase
import { NetworkCanvas } from './NetworkCanvas';

// 3. 状态管理 - 使用Zustand
const useAppStore = create<AppState>()(subscribeWithSelector((set) => ({
  warMode: false,
  setWarMode: (mode) => set({ warMode: mode }),
})));
```

---

## 六、环境配置

### 6.1 开发环境

```bash
# 启动所有服务
docker-compose -f docker-compose.dev.yml up -d

# 访问地址
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- Neo4j: http://localhost:7474
- PostgreSQL: localhost:5432
- Redis: localhost:6379
```

### 6.2 环境变量

详见 `.env.example` 文件。

---

## 七、开发工作流

### 7.1 会话启动流程

1. 运行 `git status` 检查代码库状态
2. 读取 `progress.md` 了解开发进度
3. 读取 `features.json` 选择本次任务
4. 运行 `scripts/init.sh` 启动开发环境

### 7.2 代码提交规则

- 后端代码: `backend: [模块] 功能描述`
- 前端代码: `frontend: [组件] 功能描述`
- 文档更新: `docs: 更新内容`

### 7.3 功能验证

每个功能必须通过 `features.json` 中定义的测试步骤验证后才能标记为完成。

---

## 八、联系与支持

- 项目仓库: https://github.com/wr5912/AI-SecOps
- 问题反馈: 请提交Issue

---

**最后更新**: 2026-03-14
**维护者**: AI-SecOps开发团队
