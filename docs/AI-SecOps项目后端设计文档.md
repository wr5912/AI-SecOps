# AI-SecOps 企业智能安全运营平台 - 后端引擎与控制面详细设计文档

## 文档信息

| 属性     | 内容                                                        |
| -------- | ----------------------------------------------------------- |
| 版本     | v2.0.0                             |
| 项目名称 | AI-SecOps                                                   |
| 核心定位 | 原生 Open XDR 数据引擎 + Agentic SOAR 编排中枢 + BFF 控制面 |
| 文档类型 | 后端详细设计规格说明书                                      |
| 适用对象 | Claude Code 及开发团队                                      |
| 创建日期 | 2026年3月14日                                               |


---

## 第一章 系统架构重塑：控制面与数据面分离

### 1.1 架构本质
本后端系统不仅为前端提供 API 支撑，更是整个企业的**网络安全数据处理引擎和自动化响应中枢**。系统在逻辑上严格划分为两大平面：
*   **数据与智能引擎面（Data & AI Plane）**：实现第一份指南中定义的“九层技术架构”。负责吞吐海量异构异构原始日志，通过 DSPy 进行大模型清洗，写入 Neo4j 知识图谱，并由 LangGraph 和 AutoGen 进行自动化编排与推演。
*   **交互控制面（Control Plane / BFF）**：基于 FastAPI 构建。负责拦截并响应前端 React 应用的请求，提供基于 RBAC 的权限控制，维护 WebSocket 长连接，处理人类在环（HITL）的审批挂起与唤醒，以及将运维人员的“误报/漏报”反馈回流至底层训练管道。

### 1.2 全局技术栈选型（深度对齐 AI Agent 生态）

| 技术类别   | 选用技术          | 选型理由（AI-SecOps 视角）                                   |
| ---------- | ----------------- | ------------------------------------------------------------ |
| API 框架   | FastAPI + Uvicorn | 原生异步，完美支持高频 WebSocket 告警推送与 SSE 流式 AI 问答 |
| 内存流数据 | Redis / Kafka     | 承载 L1防洪网关的 10万+ EPS 吞吐，解耦前后端高频刷新         |
| 图数据库   | Neo4j 5.x         | L3图谱构建，存储资产拓扑与攻击链路（Attack Graph），支撑前端拓扑画布 |
| 关系型库   | PostgreSQL 16+    | 存储用户、权限、审计日志、HITL 审批工单、持久化 LangGraph State |
| AI 提取层  | DSPy              | L2/L4 核心，取代脆弱的 Regex，实现健壮的 OCSF 实体提取和上下文压缩 |
| 编排与控制 | LangGraph         | L6 核心，构建循环 Agent 状态机，原生支持 `interrupt_before`（人类在环审批） |
| 对抗推演   | AutoGen           | L7 核心，多智能体红蓝对抗，生成防御策略                      |
| 终端协议   | OpenC2            | L8 核心，向 pi-mono 终端代理下发标准化的阻断、隔离等 JSON 指令 |

---

## 第二章 数据与智能引擎面（9层架构的后端映射）

底层的 9 层架构通过异步微服务或后台守护进程的方式运行，通过 `trace_id` 贯穿始终。

### 2.1 摄取与加工层（Layer 1 - 2）
*   **L1 防洪网关 (`layer1_flood_gate`)**：采用 Aho-Corasick 算法的 Python 扩展，提供高速 Webhook 端点 `POST /ingress/syslog` 接收深信服、Palo Alto 等设备日志。将高置信度事件打上 `trace_id` 并推入 Kafka/Redis 流。
*   **L2 数据清洗 (`layer2_normalizer`)**：后台消费流数据，调用 DSPy 将异构日志映射为 **OCSF (Open Cybersecurity Schema Framework)** 标准 JSON，并存入 PostgreSQL。

### 2.2 关联与分析层（Layer 3 - 5）
*   **L3 知识图谱 (`layer3_graph`)**：将 OCSF 实体（IP、Domain、User）作为 Node，事件作为 Edge，写入 Neo4j。前端 React Flow 获取的节点和连线数据直接来源于此层的 Graph Query (Cypher)。
*   **L4 信息压缩 (`layer4_compression`)**：面对前端渲染压力，此层基于时间窗口将多条碎日志压缩为一个“告警故事线（Storyline）”超级节点。
*   **L5 智能研判 (`layer5_analyzer`)**：LLM 虚拟专家，输出包含 `confidence_score`、`mitre_tactics` 和 `analysis_reasoning`（思维链）的研判报告，该报告将展示在前端的 AI Copilot 卡片中。

### 2.3 决策与执行层（Layer 6 - 8）
*   **L6 控制编排 (`layer6_orchestrator`)**：基于 LangGraph 运行标准 SOAR 剧本。这是连接前端的**核心枢纽**：当剧本判定需要“阻断核心路由器”，LangGraph 触发 `interrupt`，状态存入 Postgres，并通过 WebSocket 通知前端弹窗拦截。
*   **L7 对抗推演 (`layer7_simulator`)**：在后台用 AutoGen 根据图谱预测攻击路径，生成的数据用于前端“战时模式（War Mode）”的红色预警路径高亮。
*   **L8 终端执行 (`layer8_executor`)**：提供南向接口，将编排指令翻译为 OpenC2 格式，下发给各网络终端的 pi-mono agent。

---

## 第三章 BFF 控制面：FastAPI 接口设计（面向前端）

API 设计严格围绕前端的 `Zustand` 状态管理和高频交互展开。

### 3.1 核心数据交互协议设计
所有核心实体（告警、动作、日志）必须包含 `trace_id`。
统一的响应封装结构：
```python
class APIResponse(BaseModel):
    trace_id: str          # 贯穿全程的追踪ID
    success: bool
    data: Any
    meta: dict = {}        # 可包含翻页、用时、置信度等元数据
```

### 3.2 动态拓扑与资产接口 (Neo4j 驱动)
为前端 React Flow 提供高度优化的数据，支持 Clustering（聚合）以防前端卡死。
| 方法   | 路径                                 | 描述                                                        |
| ------ | ------------------------------------ | ----------------------------------------------------------- |
| `GET`  | `/api/v1/topology/graph`             | 获取网络拓扑，支持 `zoom_level` 参数实现节点动态聚合        |
| `GET`  | `/api/v1/assets/{asset_id}/hologram` | 获取 360 度全息资产卡片详情（聚合资产、漏洞、负责人员信息） |
| `POST` | `/api/v1/assets/{asset_id}/actions`  | 一键操作（如隔离），此接口将指令发往 L8 终端执行层          |

### 3.3 人机协同 (HITL) 与审批闭环
当 LangGraph (L6) 挂起时，与前端交互的专门 API。
| 方法   | 路径                                       | 描述                                                        |
| ------ | ------------------------------------------ | ----------------------------------------------------------- |
| `GET`  | `/api/v1/orchestration/pending`            | 获取当前等待人类审批的高危动作列表                          |
| `POST` | `/api/v1/orchestration/{trace_id}/approve` | 前端点击【同意】，唤醒 LangGraph 继续执行 `OpenC2` 阻断指令 |
| `POST` | `/api/v1/orchestration/{trace_id}/reject`  | 前端点击【拒绝】，LangGraph 路由至降级处理节点              |

### 3.4 “运营即训练” 反馈回流接口
对应前端卡片上的 👍/👎 或“标记为误报”按钮，数据将直接流入底层 DSPy 的 Few-Shot 样本库中。
| 方法   | 路径                          | 描述                                                         |
| ------ | ----------------------------- | ------------------------------------------------------------ |
| `POST` | `/api/v1/feedback/submit`     | 提交包含 `trace_id`、`feedback_type`（如 false_positive）的评估 |
| `POST` | `/api/v1/feedback/correction` | 资深分析师手工修正 AI 的研判结论（TTPs 映射等）              |

### 3.5 AI Copilot SSE 与大模型交互接口
| 方法  | 路径                          | 描述                                                         |
| ----- | ----------------------------- | ------------------------------------------------------------ |
| `GET` | `/api/v1/copilot/chat/stream` | (SSE) 提供打字机效果的对话。系统会自动将前端选中的 `asset_id` 作为上下文注入 RAG |

---

## 第四章 高频实时通信设计（WebSocket 架构）

在 AI-SecOps 中，前端的“平战双模式”切换和告警高亮极度依赖低延迟的推送。

### 4.1 WebSocket 架构模型
后端采用 `FastAPI WebSocket` + `Redis Pub/Sub` 架构。
前端的 Zustand store 建立连接后，订阅特定的频道（如 `soc_global_alerts`, `hitl_approvals`）。

### 4.2 推送消息结构 (Payload)
为了避免 React Flow 整个画布重绘，后端推送的数据必须是增量的、细粒度的指令，前端 Zustand 接收后直接按 ID 更新对应节点状态。
```json
// 后端推送示例：战时模式下的资产状态变更
{
  "type": "ASSET_STATUS_UPDATE",
  "trace_id": "trk-5f9a2b",
  "payload": {
    "asset_id": "srv-db-001",
    "new_status": "compromised",
    "trigger_war_mode": true,
    "glow_color": "#EF4444"
  }
}
```

```json
// 后端推送示例：新的高危阻断需要审批
{
  "type": "HITL_APPROVAL_REQUIRED",
  "trace_id": "trk-7c3d11",
  "payload": {
    "action": "isolate_network",
    "target_ip": "10.0.0.5",
    "risk_assessment": "阻断可能导致核心业务中断5分钟",
    "timeout": 300 // 5分钟内不审批则默认放弃
  }
}
```

---

## 第五章 核心数据模型 (Pydantic & ORM)

### 5.1 OCSF 标准化告警模型 (Pydantic)
所有经过 L2 层清洗的数据，以及暴露给前端的告警数据，均符合此结构：
```python
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class OCSFObservable(BaseModel):
    name: str  # e.g., "ip", "hostname"
    value: str

class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class NormalizedIncident(BaseModel):
    trace_id: str
    category_uid: int
    category_name: str
    time: str
    observables: List[OCSFObservable]
    attacker_ip: Optional[str] = None
    victim_ip: Optional[str] = None
    summary: str
    confidence_score: float
    severity: AlertSeverity = AlertSeverity.MEDIUM
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
```

### 5.2 资产数据模型 (Pydantic)
**⚠️ 新增**：根据前后端协同核对报告，补充完整的Asset模型定义。与前端TypeScript模型完全对齐。
```python
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class AssetType(str, Enum):
    SERVER = "server"
    ENDPOINT = "endpoint"
    DATABASE = "database"
    FIREWALL = "firewall"
    IOT = "iot"
    CLOUD = "cloud"

class AssetStatus(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    COMPROMISED = "compromised"

class AssetVulnerability(BaseModel):
    cvss: float
    name: str

class Asset(BaseModel):
    # 资产唯一标识符
    id: str
    # 贯穿全程的追踪ID（必填）
    trace_id: str
    # 资产显示名称
    name: str
    # IP地址
    ip: str
    # 资产类型
    type: AssetType
    # 资产状态
    status: AssetStatus
    # 风险评分（0-100）
    risk_score: int
    # 操作系统信息
    os: str
    # 所属部门
    department: str
    # 资产负责人
    owner: str
    # 开放端口列表
    ports: List[int] = []
    # 漏洞列表
    vulnerabilities: List[AssetVulnerability] = []
    # 关联的资产ID列表
    connections: List[str] = []
```

### 5.3 故事线数据模型 (Pydantic)
**⚠️ 新增**：根据前后端协同核对报告，补充完整的Storyline模型定义。与前端TypeScript模型完全对齐。
```python
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class StorylineSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"

class StorylineStatus(str, Enum):
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"

class StorylineStep(BaseModel):
    time: str
    event: str
    node: str

class Storyline(BaseModel):
    # 故事线唯一标识符
    id: str
    # 贯穿全程的追踪ID（必填）
    trace_id: str
    # 故事线标题
    title: str
    # 故事线描述
    description: str
    # 严重程度
    severity: StorylineSeverity
    # 置信度（0-100）
    confidence_score: float
    # 涉及的资产ID列表
    assets: List[str]
    # MITRE ATT&CK战术ID列表
    mitre_tactics: List[str] = []
    # 攻击步骤时间线
    steps: List[StorylineStep]
    # 处理状态
    status: StorylineStatus
```

### 5.4 状态机持久化模型 (PostgreSQL)
用于支持 L6 层的 LangGraph 断点续跑和前端历史工单查询。
```python
# SQLAlchemy Model
class WorkflowState(Base):
    __tablename__ = "workflow_states"
    
    trace_id = Column(String, primary_key=True, index=True)
    current_node = Column(String, nullable=False) # 例如 "awaiting_human_approval"
    state_json = Column(JSONB, nullable=False)    # 存储图的完整状态快照
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## 第六章 后端项目目录结构 (融合 9 层与 API)

严格按照 Harness Engineering 规范，后端仓库结构需清晰划分数据平面与控制平面：

```
backend/
├── src/
│   ├── api/                     # 【交互控制面 (BFF)】
│   │   ├── routers/             # FastAPI 路由 (assets, alerts, hitl, copilot)
│   │   ├── websockets/          # WebSocket 管理器与 Redis 订阅器
│   │   ├── middlewares/         # 鉴权 (JWT, RBAC)、限流
│   │   └── dependencies.py      # 数据库 Session、用户上下文注入
│   ├── data_plane/              # 【数据与智能引擎面 (9层架构)】
│   │   ├── layer1_flood_gate/   # Webhook 接收与 Sigma 降噪引擎
│   │   ├── layer2_normalizer/   # DSPy 日志清洗，转 OCSF
│   │   ├── layer3_graph/        # Neo4j 知识图谱构建与 Cypher 查询库
│   │   ├── layer4_compression/  # 时序数据与告警聚合
│   │   ├── layer5_analyzer/     # DSPy/LangChain 研判大模型提示词库
│   │   ├── layer6_orchestrator/ # LangGraph 剧本定义与状态机
│   │   ├── layer7_simulator/    # AutoGen 多 Agent 红蓝对抗逻辑
│   │   ├── layer8_executor/     # OpenC2 指令封装与 pi-mono 终端通信
│   │   └── layer9_reporter/     # 审计日志合规与报表生成
│   ├── core/                    # 通用基础设施 (Config, Auth, Security)
│   └── models/                  # Pydantic 实体与 SQLAlchemy 映射
├── tests/
├── alembic/                     # 数据库迁移
└── pyproject.toml
```

---

## 第七章 安全与性能考量

### 7.1 图数据库防刷与限流 (Graph Query Protection)
由于前端可以探索极其庞大的网络拓扑（L3 Neo4j），API 必须防止指数级的查询爆炸（如 `MATCH (n)-[*1..10]-(m)`）。
*   **策略**：在 API 层强制设置查询深度限制（`max_depth=3`），并对拓扑查询接口实施严格的 IP/User Token 限流（Rate Limiting）。

### 7.2 提示词注入防护 (Prompt Injection)
前端通过 AI Copilot 传入的自然语言（甚至恶意攻击者在原始日志中夹带的恶意 Payload）将直接进入 L5/L6 的大模型。
*   **策略**：所有进入 LLM 的输入必须经过 Pydantic 严格过滤清洗，严禁 LLM 直接生成并执行 Python 代码或 Shell 脚本，所有执行必须通过严格定义的 OpenC2 JSON 格式进入 L8 终端执行层，且高危指令强制触发 HITL。

### 7.3 并发与状态一致性 (State Consistency)
在多操作员协同的 SOC 场景中，两名分析师可能同时对同一个告警故事线（Storyline）进行处置。
*   **策略**：对于 L6 LangGraph 状态机的唤醒（Approve/Reject）以及资产状态更新，采用 PostgreSQL 的乐观锁（Optimistic Locking）机制。结合版本号（`version` 字段），当检测到状态冲突时，后端返回 `409 Conflict`，前端 Zustand 收到后提示用户“该事件已被其他分析师处理”，并自动刷新最新状态。

---

## 第八章 核心业务数据流（端到端工作流）

为了清晰展示后端引擎（9层架构）与控制面（API+WebSocket）以及前端的协同工作机制，以下定义三个核心业务场景的数据流转图：

### 8.1 场景一：高危威胁突发与“战时模式”触发流
1. **[L1 防洪网关]** 接收到防火墙 Webhook 的海量异常流量日志，通过 Sigma 规则初筛。
2. **[L2 数据清洗]** DSPy 提取出源 IP 和目标资产，格式化为 OCSF 标准。
3. **[L3/L4 关联压缩]** 发现该源 IP 正在对核心数据库（`asset_id: db-001`）进行横向移动，压缩生成高危故事线（Storyline）。
4. **[L5 智能研判]** 大模型判定该行为符合 MITRE `T1021`（远程服务利用），置信度 `0.95`。
5. **[API 控制面]** WebSocket 立即向前端广播 `WAR_MODE_TRIGGERED` 和 `NEW_STORYLINE` 消息。
6. **[前端 React]** Zustand 监听到消息，界面色调瞬间切换为红黑，拓扑图（React Flow）将 `db-001` 节点标红闪烁，并自动弹出 AI Copilot 分析报告。

### 8.2 场景二：人类在环 (HITL) 自动化审批流
1. **[L6 控制编排]** 针对上述场景，LangGraph 开始执行剧本。执行到“封禁外部 IP”节点时，自动通过；执行到“隔离内网数据库”节点时，触发 `interrupt_before` 挂起。
2. **[API 控制面]** 生成挂起工单，写入 PostgreSQL，并通过 WebSocket 推送 `HITL_APPROVAL_REQUIRED` 弹窗。
3. **[前端 React]** 分析师在卡片上点击【批准隔离】，前端调用 `POST /api/v1/orchestration/{trace_id}/approve`。
4. **[API 控制面]** 鉴权通过后，从 DB 恢复 LangGraph 状态，继续执行图逻辑。
5. **[L8 终端执行]** 生成标准 OpenC2 隔离指令：`{"action": "deny", "target": {"ipv4_net": "10.0.0.5"}}`，下发给终端 pi-mono 代理执行。

### 8.3 场景三：“运营即训练”的反馈回流闭环
1. **[前端 React]** 分析师发现某个告警是内部漏扫工具触发的，点击【标记为误报】。前端调用 `POST /api/v1/feedback/submit`。
2. **[API 控制面]** 接收包含 `trace_id` 的反馈，写入 PostgreSQL 历史记录。
3. **[L9 复盘研报]** 后台异步任务提取该 `trace_id` 对应的原始日志和 OCSF 映射。
4. **[L5 智能研判]** DSPy 的 `Teleprompter`（优化器）在夜间例行任务中，提取这批被标记为误报的样本，动态更新 Few-Shot Prompt 模板，明天相同的扫描行为将不再触发高危告警。

---

## 第九章 部署架构与环境要求

作为高度 AI 化的数据处理引擎，本后端的资源消耗特征与传统 Web 服务截然不同，它兼具**高 I/O（流处理）**与**高计算（图查询与 LLM 推理）**特征。

### 9.1 基础设施架构
采用云原生容器化部署（Docker + Kubernetes）：
*   **API Pods (FastAPI)**：无状态横向扩展，配置 HPA（按 CPU 使用率自动扩缩容）。
*   **Worker Pods (Celery/LangGraph)**：消费队列任务，负责重度执行逻辑。
*   **DSPy/AI Pods**：若采用本地私有化大模型（如 Qwen/Llama3），需调度至具备 Nvidia GPU 的节点；若调用闭源大模型 API（如 GPT-4/Claude 3），则仅需普通 CPU 节点。

### 9.2 核心中间件调优
*   **Neo4j 5.x**：由于频繁进行拓扑和路径查询，必须为 OCSF 实体的 `ip`, `hostname`, `user` 等属性建立全文索引（Full-text Index）和节点标签索引。推荐分配至少 16GB 的 Page Cache 内存。
*   **Redis**：用于 WebSocket 的 Pub/Sub 频道和防洪网关的缓冲队列，需开启持久化（AOF）以防极端情况下的状态丢失。
*   **PostgreSQL 16+**：优化 `JSONB` 字段查询，为 `trace_id` 和 `status` 字段建立 GIN 和 B-Tree 索引。

### 9.3 环境变量与配置矩阵 (`.env`)
```bash
# --- 1. BFF 控制面配置 ---
API_PORT=8000
WORKERS=4
SECRET_KEY="super_secret_jwt_key_here"
CORS_ORIGINS="http://localhost:5173,https://soc.company.internal"

# --- 2. 数据库与图谱存储 (L3 & 存储) ---
NEO4J_URI="bolt://neo4j-server:7687"
NEO4J_AUTH="neo4j/very_secure_password"
POSTGRES_URL="postgresql+asyncpg://usr:pwd@pg-server/ai_secops"
REDIS_URL="redis://redis-server:6379/0"

# --- 3. AI 与大模型引擎 (L2 & L5) ---
LLM_PROVIDER="openai" # 或 "vllm", "azure"
LLM_API_KEY="sk-..."
LLM_MODEL_NAME="gpt-4o"
DSPY_CACHE_DIR="/var/cache/dspy"

# --- 4. 终端执行层 (L8) ---
OPENC2_BROKER_URL="mqtt://internal-mqtt-broker:1883"
```

---

## 第十章 Harness Engineering 质量保证体系

作为 OpenClaw / AI Agent 开发的企业级项目，后端的测试必须遵循第一份指南中的 Harness Engineering 原则。

### 10.1 Linter 与架构约束强制检查
使用 `ruff` 配置严格的检查规则，**禁止跨层调用**（如 API 层直接导入 L8 终端执行层的内部函数）。
```toml
# pyproject.toml 示例
[tool.ruff.lint.custom-rules]
no-api-to-l8-imports = { message = "架构约束：禁止 API 层绕过 L6 控制编排直接调用 L8 终端执行" }
```

### 10.2 DSPy 确定性断言测试 (Deterministic Testing)
AI 具有不确定性，必须对其输出（如 OCSF 结构）进行强制校验。
利用 `pytest` 编写专门的提示词验证测试集，注入已知的恶意日志，断言 L2 层是否稳定输出了包含必需字段（如 `attacker_ip`）的 JSON。

### 10.3 Agent 编排的集成测试 (LangGraph Mocking)
测试 L6 层的 SOAR 剧本时，不应该真的去隔离物理主机的 IP。
*   **策略**：构建专门的 `MockXDRAdapter` 和 `MockTerminalAgent`。在 CI 管道中，运行 E2E 测试时，验证 LangGraph 是否按预期正确到达了 `interrupt_before` 节点，且其生成的 OpenC2 Payload 格式是否完全符合规范。

---

---

## 第十一章 前后端共享数据模型Schema策略

### 11.1 统一建模原则

根据前后端协同核对报告（2026年3月），为确保前后端数据模型的一致性，采用以下建模原则：

| 原则 | 描述 |
|------|------|
| **单一真相源（SSOT）** | 后端Pydantic模型作为唯一真实数据源，前端TypeScript接口从中自动生成 |
| **命名规范统一** | 所有JSON传输字段使用snake_case，后端Python代码使用snake_case，前端TypeScript内部变量可使用camelCase但必须支持snake_case转换 |
| **必填字段标记** | 所有核心实体必须包含`trace_id`字段，确保分布式追踪能力 |

### 11.2 字段命名映射表

为解决前后端字段命名不一致问题，定义以下统一的字段映射规则：

| 概念 | 前端TypeScript | 后端Pydantic | 说明 |
|------|----------------|---------------|------|
| 追踪ID | `trace_id` | `trace_id` | 贯穿全程，必填 |
| 告警级别 | `severity` | `severity` | critical/high/medium/low |
| 攻击源IP | `attacker_ip` | `attacker_ip` | 网络层面的源地址 |
| 攻击目标IP | `victim_ip` | `victim_ip` | 网络层面的目标地址 |
| 置信度 | `confidence_score` | `confidence_score` | 0-100数值 |
| 风险评分 | `risk_score` | `risk_score` | 资产风险评分 |
| MITRE战术 | `mitre_tactic` | `mitre_tactic` | MITRE ATT&CK战术ID |
| 故事线ID | `storyline_id` | `storyline_id` | 关联的故事线 |

### 11.3 自动生成策略

**⚠️ 推荐实施**：使用`datamodel-code-generator`工具在CI/CD流程中自动从Pydantic模型生成TypeScript接口。

```bash
# 安装工具
pip install datamodel-code-generator

# 生成TypeScript接口
datamodel-code-generator \
  --input model.py \
  --output ../frontend/src/types/generated.ts \
  --output-model-type TypeScriptModel \
  --enum-type enum
```

### 11.4 API响应封装规范

所有API响应必须包含`trace_id`，以便前端进行请求追踪：

```python
class APIResponse(BaseModel):
    trace_id: str          # 贯穿全程的追踪ID
    success: bool
    data: Any
    meta: dict = {}        # 可包含翻页、用时、置信度等元数据
```

---

*本文档版本：v2.1.0 (协同修复版)*
*最后更新：2026年3月14日*