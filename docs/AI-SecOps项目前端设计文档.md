# AI-SecOps 企业智能安全运营平台 - 前端详细设计文档

## 文档信息

| 属性 | 内容 |
|------|------|
| 版本 | v1.0.0 |
| 项目名称 | AI-SecOps SOC Platform |
| 文档类型 | 前端详细设计规格说明书 |
| 适用对象 | Claude Code 及开发团队 |
| 创建日期 | 2026年3月14日 |

---

## 第一章 项目概述

### 1.1 项目背景与定位

AI-SecOps 是为企业级安全运营中心（SOC）设计的智能网络安全态势感知与响应平台。该平台的核心使命是为网络安全运维人员提供一个统一、直观且高效的「单一窗口」工作界面，用于监控、检测、分析和响应企业网络安全威胁。平台集成了传统SIEM（安全信息与事件管理）能力与前沿的AI驱动决策支持系统，同时提供直观的攻击可视化功能，帮助安全团队在复杂的网络环境中快速定位威胁、理解攻击链路并采取有效的响应措施。

项目的目标用户群体包括：SOC一级至三级分析师、事件响应人员、CISO（首席信息安全官）以及安全工程师。该平台设计充分考虑了不同角色用户的差异化需求，从一线分析师的日常监控工作到CISO的战略决策支持，提供了一套完整的安全运营解决方案。

### 1.2 核心设计理念

本项目的设计哲学围绕「动态画布加AI副驾驶」（Dynamic Canvas + AI Copilot）的核心模式展开，这一设计理念旨在彻底改变传统安全运营界面的静态展示方式，通过交互式网络拓扑画布与智能AI助手的有机结合，为用户提供更加直观、高效且智能的安全运营体验。

首先，动态网络拓扑画布作为整个平台的核心交互界面，取代了传统的静态仪表板布局。通过采用开源稳定的React Flow组件库，构建支持缩放、拖拽和平移的交互式网络拓扑视图，使安全运维人员能够以直观的方式观察网络资产之间的连接关系、攻击路径以及实时安全状态。这种动态可视化方式不仅提升了用户对复杂网络拓扑的理解效率，还支持点击节点查看详细资产信息、拖拽连接建立新的网络关系等交互操作。

其次，AI Copilot智能助手作为平台的第二大核心组件，提供了一个上下文感知的对话界面。安全分析师可以直接与AI助手交互，获取威胁分析、攻击链路解读、响应建议、威胁情报查询等服务。AI助手能够理解当前选中的资产上下文，提供针对性的分析和建议，大大缩短了威胁研判的时间。

第三，告警故事情节（Alert Storyline）视图是解决告警疲劳问题的创新方案。传统的安全运营界面往往堆砌大量独立告警，使分析师陷入信息过载的困境。本平台通过将相关告警聚合为攻击故事线，以时间线的形式展示攻击的全过程，帮助分析师从宏观角度理解攻击事件的完整链路，从而更高效地进行威胁研判和响应决策。

第四，360度资产全息卡片为每个网络资产提供全方位的上下文信息展示。当用户点击画布上的资产节点时，会弹出详细的信息卡片，包含资产的基本信息、风险评分、漏洞信息、开放端口、所属部门、资产所有者等丰富内容，同时提供一键隔离、封禁IP、漏洞扫描等快速响应操作入口。

第五，平战一体双模式设计（Peace/War Mode）是平台的特色功能之一。平时模式（Peace Mode）采用冷静的蓝绿色调，展示日常安全监控界面；战时模式（War Mode）则切换为红黑色调，配合警报闪烁、红色光晕等视觉效果，直观展示当前威胁等级和攻击态势，支持快速决策和应急响应。

### 1.3 技术栈选型

本项目采用现代化的前端技术栈构建，确保高性能、可维护性和良好的开发体验。核心技术选型如下：

| 技术类别 | 选用技术 | 版本要求 | 选型理由 |
|----------|----------|----------|----------|
| 框架 | React | ^18.2.0 | 成熟的组件化UI框架，生态系统丰富，适合构建复杂的企业级应用 |
| 语言 | TypeScript | ^5.3.3 | 提供完整的类型系统，增强代码可维护性和重构安全性 |
| 构建工具 | Vite | ^5.0.8 | 极速的开发服务器启动和热更新体验，生产构建效率高 |
| 样式方案 | Tailwind CSS | ^3.3.6 | 原子化CSS框架，支持响应式设计，快速构建现代UI |
| 网络拓扑 | @xyflow/react | ^12.0.0 | React Flow的最新版，稳定可靠，支持复杂的节点和边定制 |
| 图标库 | lucide-react | ^0.294.0 | 现代化图标库，风格统一，易于定制 |
| 图表库 | recharts | ^2.10.3 | React原生的图表库，灵活且易于定制 |

---

## 第二章 技术架构设计

### 2.1 项目结构规范

项目采用标准的React项目结构，结合TypeScript的模块化特性，确保代码组织清晰、易于维护。以下是推荐的项目目录结构：

```
cyber-sentinel/
├── src/
│   ├── components/              # 可复用UI组件目录
│   │   ├── common/             # 通用基础组件
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   ├── Input/
│   │   │   ├── Modal/
│   │   │   └── ...
│   │   ├── layout/            # 布局组件
│   │   │   ├── Header/
│   │   │   ├── Sidebar/
│   │   │   └── ...
│   │   ├── network/           # 网络拓扑相关组件
│   │   │   ├── NetworkCanvas/
│   │   │   ├── nodes/         # 自定义节点组件
│   │   │   │   ├── ServerNode.tsx
│   │   │   │   ├── FirewallNode.tsx
│   │   │   │   ├── DatabaseNode.tsx
│   │   │   │   ├── EndpointNode.tsx
│   │   │   │   ├── IoTNode.tsx
│   │   │   │   └── CloudNode.tsx
│   │   │   └── edges/         # 自定义边组件
│   │   ├── copilot/           # AI Copilot组件
│   │   │   ├── ChatPanel/
│   │   │   ├── MessageBubble/
│   │   │   └── QuickActions/
│   │   ├── storyline/         # 告警故事线组件
│   │   │   ├── StorylineCard/
│   │   │   ├── Timeline/
│   │   │   └── ...
│   │   └── asset/             # 资产相关组件
│   │       ├── AssetCard/
│   │       ├── AssetList/
│   │       └── ...
│   ├── hooks/                 # 自定义Hooks目录
│   │   ├── useNetworkTopology.ts
│   │   ├── useAIChat.ts
│   │   ├── useWarMode.ts
│   │   ├── useKeyboard.ts
│   │   └── ...
│   ├── contexts/              # React Context目录
│   │   ├── WarModeContext.tsx
│   │   ├── ThemeContext.tsx
│   │   └── SelectionContext.tsx
│   ├── services/               # API服务层
│   │   ├── api.ts
│   │   ├── assets.ts
│   │   ├── alerts.ts
│   │   └── threatIntelligence.ts
│   ├── types/                  # TypeScript类型定义
│   │   ├── index.ts
│   │   ├── asset.ts
│   │   ├── alert.ts
│   │   └── ...
│   ├── utils/                  # 工具函数
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   ├── data/                   # 模拟数据
│   │   └── mockData.ts
│   ├── App.tsx                 # 主应用组件
│   ├── main.tsx                # 应用入口
│   └── index.css               # 全局样式
├── public/                     # 静态资源
├── dist/                       # 构建输出
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── SPEC.md                     # 项目规格说明
```

### 2.2 组件架构原则

本项目采用组件化架构设计，遵循以下核心原则以确保代码的可维护性、可扩展性和可测试性。

**单一职责原则（SRP）**：每个组件应当有且只有一个改变的原因。在实际实现中，这意味着将大型组件拆分为更小的、可复用的单元。例如，NetworkCanvas组件专注于网络拓扑的渲染逻辑，而具体的节点渲染则委托给专门的Node组件（如ServerNode、FirewallNode等）。这种拆分使得每个组件的职责清晰，便于单独测试和维护。

**开闭原则（OCP）**：软件实体应当对扩展开放，对修改关闭。在本项目中，这通过React的组件组合和props设计来实现。例如，NetworkCanvas组件通过nodeTypes和edgeTypes props接收不同类型的节点和边配置，使得添加新的节点类型时无需修改NetworkCanvas本身，只需创建新的节点组件并注册即可。

**依赖倒置原则（DIP）**：高层模块不应依赖低层模块，两者都应依赖抽象。在实际编码中，这意味着应当依赖于接口（TypeScript的type或interface）而不是具体实现。例如，组件应当依赖于Asset接口定义的资产数据结构，而不是直接依赖于mockAssets这样的具体数据源。这样可以轻松切换数据源而不影响组件逻辑。

**组合优于继承**：React的组件模型天然支持组合模式。本项目大量使用组件组合来实现功能复用和逻辑复用。例如，NetworkCanvas内部组合了Background、Controls、MiniMap等子组件，通过props传递配置参数，实现了功能的高度可定制性。

### 2.3 状态管理策略

本项目根据不同场景采用分层的状态管理策略，平衡复杂度与性能需求。

**本地组件状态（useState）**：对于仅在单个组件内部使用的状态，如弹窗的显示隐藏、输入框的值、加载状态等，优先使用React的useState hook。这是最简单的状态管理方式，适用于低复杂度场景。

**跨组件状态（Context）**：对于需要在多个组件之间共享的状态，如战争/和平模式切换（warMode）、当前选中的资产（selectedAsset）、当前选中的故事线（selectedStoryline）等，使用React Context进行管理。本项目定义了WarModeContext、SelectionContext等上下文，提供跨组件的状态共享能力。

**派生状态（useMemo）**：对于需要基于其他状态计算得出的值，使用useMemo进行缓存优化。例如，网络拓扑的节点数据（initialNodes）需要根据assets数组、warMode状态、selectedAsset等计算得出，使用useMemo可以避免不必要的重复计算，提升渲染性能。

**副作用处理（useEffect）**：对于需要处理副作用的操作，如订阅外部数据源、设置定时器、操作DOM等，使用useEffect hook。例如，HUD组件中的当前时间显示就需要使用useEffect设置定时器进行每秒更新。

### 2.4 数据流架构

本项目采用单向数据流架构，数据从父组件向子组件通过props传递，子组件通过回调函数向父组件传递事件和请求。这种架构使得数据流向清晰可追溯，便于调试和维护。

具体而言，App作为根组件，承担着状态容器的角色，持有所有核心业务状态（warMode、selectedAsset、selectedAsset等），并通过props将这些状态和状态更新函数传递给子组件。子组件在需要更新状态时，调用父组件传递的回调函数，由父组件统一处理状态更新逻辑。这种设计确保了状态变更的可控性和可预测性。

---

## 第三章 核心组件规格说明

### 3.1 网络拓扑画布组件（NetworkCanvas）

#### 3.1.1 组件概述

NetworkCanvas是整个平台的核心可视化组件，基于@xyflow/react（React Flow）库构建，提供交互式的网络拓扑图展示能力。该组件负责渲染企业网络中的各类资产节点、节点之间的连接关系，并支持用户通过缩放、拖拽、点击等交互操作探索网络拓扑。

#### 3.1.2 核心功能

| 功能名称 | 功能描述 | 实现要点 |
|----------|----------|----------|
| 节点渲染 | 在画布上渲染各类网络资产节点 | 使用自定义节点组件（ServerNode、FirewallNode等），根据资产类型渲染不同外观 |
| 边渲染 | 展示资产之间的网络连接关系 | 使用Edge组件，支持普通连接和攻击路径的差异化渲染 |
| 缩放功能 | 支持画布缩放以查看不同细节层次 | 集成React Flow的Controls组件，提供缩放按钮和滑块 |
| 拖拽功能 | 支持拖拽画布查看不同区域 | React Flow默认支持，可通过minZoom和maxZoom限制缩放范围 |
| 节点点击 | 点击节点选中资产并显示详情 | 通过onNodeClick回调处理节点点击事件 |
| 节点连接 | 支持拖拽创建新的节点连接 | 通过onConnect回调处理连接创建 |
| 小地图 | 显示全局拓扑概览和当前位置 | 集成MiniMap组件，提供导航能力 |

#### 3.1.3 Props接口定义

```typescript
interface NetworkCanvasProps {
  // 资产数据列表
  assets: Asset[];
  // 告警数据列表
  alerts: Alert[];
  // 当前选中的资产ID
  selectedAsset: string | null;
  // 资产选中回调函数
  onSelectAsset: (id: string | null) => void;
  // 是否处于战争模式
  warMode: boolean;
  // 当前选中的故事线（用于高亮攻击路径）
  storyline: Storyline | null;
}
```

#### 3.1.4 节点类型配置

项目定义了六种自定义节点类型，分别对应不同的网络资产类别：

| 节点类型 | 资产类别 | 图标组件 | 特征 |
|----------|----------|----------|------|
| server | 服务器 | Server | 圆角矩形，带服务器图标 |
| firewall | 防火墙 | Shield | 圆角矩形，带盾牌图标，边框为琥珀色 |
| database | 数据库 | Database | 圆角矩形，带数据库图标，边框为紫色 |
| endpoint | 终端设备 | Smartphone | 圆形节点，带手机图标 |
| iot | 物联网设备 | Wifi | 圆角方形，带WiFi图标 |
| cloud | 云服务 | Cloud | 圆角方形，带云图标 |

每种节点组件都需要接收包含以下字段的data对象：label（资产名称）、ip（IP地址）、status（资产状态：normal/warning/critical/compromised）、warMode（是否战争模式）、isInStoryline（是否在当前攻击故事线中）、isSelected（是否被选中）。

#### 3.1.5 样式规格

节点的基础样式规格如下：最小宽度140-160像素，内边距12像素16像素，圆角8-12像素，边框宽度2像素。正常状态下边框颜色为slate-600（平时模式）或red-500/50（战争模式）；选中状态下边框颜色为cyan-400/amber-400/purple-400等主题色（平时模式）或red-500（战争模式），并带有发光效果（box-shadow）。

### 3.2 AI Copilot组件（AICopilot）

#### 3.2.1 组件概述

AICopilot是平台的智能助手组件，提供基于AI的安全分析和决策支持服务。该组件以侧边栏形式呈现，支持展开/收起操作，为用户提供自然语言交互界面，获取威胁分析、响应建议、情报查询等帮助。

#### 3.2.2 核心功能

| 功能名称 | 功能描述 | 实现要点 |
|----------|----------|----------|
| 聊天界面 | 提供自然语言对话交互 | 使用消息列表展示对话内容，支持用户消息和AI回复 |
| 快速操作 | 提供预设的问题模板 | 快速操作按钮，点击自动填入输入框 |
| 上下文感知 | 理解当前选中的资产上下文 | 当用户选中资产时，显示上下文提示 |
| 动作建议 | AI回复中包含可执行的操作 | 动作按钮，点击触发相应的安全操作 |
| 加载状态 | 显示AI处理中的状态 | 三个圆点的动画效果 |
| 消息时间 | 显示每条消息的时间戳 | 使用toLocaleTimeString格式化 |

#### 3.2.3 Props接口定义

```typescript
interface AICopilotProps {
  // 面板是否展开
  isOpen: boolean;
  // 展开/收起回调
  onToggle: () => void;
  // 当前选中的资产ID
  selectedAsset: string | null;
  // 执行动作回调
  onExecuteAction: (action: string) => void;
}
```

#### 3.2.4 消息类型定义

```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  actions?: {
    label: string;
    action: string;
  }[];
}
```

### 3.3 资产全息卡片组件（AssetHologramCard）

#### 3.3.1 组件概述

AssetHologramCard是显示选中资产详细信息的组件，以弹出卡片的形式展示资产的360度全景信息。该组件整合了资产的基本信息、风险评估、漏洞详情、开放端口等关键数据，并提供一键响应操作入口。

#### 3.3.2 核心功能

| 功能名称 | 功能描述 | 实现要点 |
|----------|----------|----------|
| 资产详情 | 显示资产的完整信息 | 名称、IP、类型、状态、风险评分 |
| 归属信息 | 显示资产的所有权信息 | 所有者、所属部门 |
| 漏洞展示 | 显示资产存在的漏洞 | 漏洞名称、Cvss评分 |
| 端口扫描 | 显示资产开放的网络端口 | 端口列表展示 |
| 快速操作 | 提供一键响应操作按钮 | 隔离主机、封禁IP、漏洞扫描、深度分析 |

#### 3.3.3 Props接口定义

```typescript
interface AssetHologramCardProps {
  // 要展示的资产对象
  asset: Asset | null;
  // 关闭回调函数
  onClose: () => void;
  // 执行动作回调函数
  onAction: (action: string) => void;
  // 是否处于战争模式
  warMode: boolean;
}
```

### 3.4 告警故事线组件（StorylinePanel）

#### 3.4.1 组件概述

StorylinePanel是解决告警疲劳问题的核心组件，通过将相关告警聚合为「攻击故事线」，以时间线卡片的形式展示完整的攻击链路。这种设计帮助分析师从宏观角度理解攻击事件的演进过程，而不是被大量独立的告警信息淹没。

#### 3.4.2 核心功能

| 功能名称 | 功能描述 | 实现要点 |
|----------|----------|----------|
| 故事线卡片 | 展示攻击故事的摘要信息 | 标题、描述、严重程度、置信度 |
| 时间线展示 | 展示攻击事件的演进过程 | 时间节点、事件描述、涉及节点 |
| MITRE映射 | 展示对应的MITRE ATT&CK战术 | 战术ID列表展示 |
| 状态指示 | 展示故事线的处理状态 | active/investigating/contained/resolved |
| 选择交互 | 支持点击选择故事线 | 高亮选中项，联动网络拓扑 |

#### 3.4.3 Props接口定义

```typescript
interface StorylinePanelProps {
  // 故事线数据列表
  storylines: Storyline[];
  // 当前选中的故事线ID
  selectedStoryline: string | null;
  // 故事线选择回调
  onSelectStoryline: (id: string | null) => void;
  // 是否处于战争模式
  warMode: boolean;
}
```

### 3.5 顶部导航栏组件（HUD）

#### 3.5.1 组件概述

HUD（Head-Up Display）组件是平台的主导航栏，提供全局搜索、威胁指数显示、模式切换、系统状态和时间信息等功能。该组件采用固定定位，始终显示在界面顶部。

#### 3.5.2 核心功能

| 功能名称 | 功能描述 | 实现要点 |
|----------|----------|----------|
| 威胁指数 | 显示当前威胁等级 | 进度条加数值的可视化展示 |
| 模式切换 | 切换和平/战争模式 | 带有图标的切换按钮 |
| 全局搜索 | 搜索资产和告警 | 带快捷键提示的搜索框 |
| 系统统计 | 显示告警数、资产数、在线率 | 图标加数字的信息展示 |
| 时间显示 | 显示当前系统时间 | 实时更新的时钟 |
| 通知铃铛 | 显示新告警通知 | 带未读红点提示 |

---

## 第四章 数据模型定义

### 4.1 资产数据模型（Asset）

```typescript
interface Asset {
  // 资产唯一标识符
  id: string;
  // 贯穿全程的追踪ID（必填）
  trace_id: string;
  // 资产显示名称
  name: string;
  // IP地址
  ip: string;
  // 资产类型
  type: 'server' | 'endpoint' | 'database' | 'firewall' | 'iot' | 'cloud';
  // 资产状态
  status: 'normal' | 'warning' | 'critical' | 'compromised';
  // 风险评分（0-100）
  risk_score: number;
  // 操作系统信息
  os: string;
  // 所属部门
  department: string;
  // 资产负责人
  owner: string;
  // 开放端口列表
  ports: number[];
  // 漏洞列表
  vulnerabilities: {
    // CVSS评分
    cvss: number;
    // 漏洞名称
    name: string;
  }[];
  // 关联的资产ID列表
  connections: string[];
}
```

### 4.2 告警数据模型（Alert）

```typescript
interface Alert {
  // 告警唯一标识符
  id: string;
  // 贯穿全程的追踪ID（必填）
  trace_id: string;
  // 告警级别
  severity: 'critical' | 'high' | 'medium' | 'low';
  // 攻击源IP地址
  attacker_ip: string;
  // 攻击目标IP地址
  victim_ip: string;
  // 告警类型描述
  type: string;
  // 告警时间
  time: string;
  // MITRE ATT&CK战术ID
  mitre_tactic: string;
  // 置信度（0-100）
  confidence_score: number;
  // 关联的故事线ID
  storyline_id?: string;
}
```

### 4.3 故事线数据模型（Storyline）

```typescript
interface Storyline {
  // 故事线唯一标识符
  id: string;
  // 贯穿全程的追踪ID（必填）
  trace_id: string;
  // 故事线标题
  title: string;
  // 故事线描述
  description: string;
  // 严重程度
  severity: 'critical' | 'high' | 'medium';
  // 置信度（0-100）
  confidence_score: number;
  // 涉及的资产ID列表
  assets: string[];
  // MITRE ATT&CK战术ID列表
  mitre_tactics: string[];
  // 攻击步骤时间线
  steps: {
    // 时间点
    time: string;
    // 事件描述
    event: string;
    // 涉及的资产ID
    node: string;
  }[];
  // 处理状态
  status: 'active' | 'investigating' | 'contained' | 'resolved';
}
```

### 4.4 聊天消息数据模型（ChatMessage）

```typescript
interface ChatMessage {
  // 消息唯一标识符
  id: string;
  // 贯穿全程的追踪ID（用于追踪对话上下文）
  trace_id: string;
  // 消息角色
  role: 'user' | 'assistant' | 'system';
  // 消息内容
  content: string;
  // 时间戳
  timestamp: Date;
  // 可执行动作列表
  actions?: {
    // 动作显示标签
    label: string;
    // 动作标识符
    action: string;
  }[];
}
```

---

## 第五章 设计系统规格

### 5.1 色彩系统

本项目定义了完整的色彩系统，确保界面的一致性和可维护性。色彩系统分为基础色彩和应用色彩两个层次。

#### 5.1.1 基础色彩

| 色彩名称 | 十六进制值 | 使用场景 |
|----------|------------|----------|
| cyber-bg | #0F172A | 主背景色，深蓝/板岩色 |
| cyber-surface | #1E293B | 卡片和表面元素背景 |
| cyber-primary | #3B82F6 | 主要操作按钮、链接 |
| cyber-danger | #EF4444 | 危险、错误、攻击告警 |
| cyber-warning | #F59E0B | 警告、可疑活动 |
| cyber-success | #10B981 | 正常、安全、成功 |
| cyber-text | #F1F5F9 | 主要文本颜色 |
| cyber-text-muted | #94A3B8 | 次要、辅助文本 |

#### 5.1.2 战争模式色彩

战争模式下，界面切换为红黑色调以强化危机感：

| 色彩名称 | 十六进制值 | 使用场景 |
|----------|------------|----------|
| war-bg | #1a0505 | 战争模式背景 |
| war-surface | #2a0a0a | 战争模式卡片 |
| war-danger | #DC2626 | 强化危险提示 |
| war-border | #7F1D1D | 战争模式边框 |

#### 5.1.3 资产状态色彩

| 状态 | 平时模式色彩 | 战争模式色彩 |
|------|--------------|--------------|
| normal | #0EA5E9 (天蓝) | #10B981 (绿) |
| warning | #F59E0B (琥珀) | #F59E0B (琥珀) |
| critical | #EF4444 (红) | #EF4444 (红) |
| compromised | #DC2626 (深红) | #DC2626 (深红) |

### 5.2 字体系统

| 字体类别 | 字体选择 | 使用场景 |
|----------|----------|----------|
| sans | Inter, system-ui | 界面UI元素、按钮、标签 |
| mono | JetBrains Mono, Fira Code | IP地址、端口号、代码、日志 |

字体大小规格：主标题24像素，副标题18像素，标签14像素，正文14像素，辅助文字12像素，小字10像素。

### 5.3 间距系统

采用4像素基准网格：4像素（xs）、8像素（sm）、12像素（md）、16像素（lg）、24像素（xl）、32像素（2xl）、48像素（3xl）。

### 5.4 视觉效果

#### 5.4.1 毛玻璃效果

```css
.glass {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(59, 130, 246, 0.2);
}
```

#### 5.4.2 发光效果

```css
.glow-danger {
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

.glow-warning {
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
}

.glow-success {
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}

.glow-primary {
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}
```

#### 5.4.3 动画效果

| 动画名称 | 效果描述 | 使用场景 |
|----------|----------|----------|
| pulse | 标准脉冲动画 | 警告闪烁、加载指示 |
| scanline | 扫描线效果 | 特殊强调效果 |
| glow | 发光呼吸效果 | 战时模式威胁指示 |

---

## 第六章 实现指南

### 6.1 开发环境搭建

#### 6.1.1 环境要求

| 软件 | 版本要求 | 说明 |
|------|----------|------|
| Node.js | >=18.0.0 | 建议使用LTS版本 |
| npm/yarn | 最新稳定版 | 推荐使用yarn |
| VS Code | 最新稳定版 | 推荐编辑器 |

#### 6.1.2 安装步骤

```bash
# 克隆项目
git clone <repository-url>
cd cyber-sentinel

# 安装依赖
yarn install

# 启动开发服务器
yarn dev
```

#### 6.1.3 开发命令

| 命令 | 功能 |
|------|------|
| yarn dev | 启动开发服务器（带热更新） |
| yarn build | 生产环境构建 |
| yarn preview | 预览生产构建结果 |

### 6.2 组件开发规范

#### 6.2.1 组件文件结构

每个组件应当有独立的文件夹，包含组件文件、类型定义、样式（如需要）：

```
ComponentName/
├── ComponentName.tsx        # 组件实现
├── ComponentName.props.ts  # Props类型定义
├── ComponentName.test.tsx  # 单元测试（可选）
└── index.ts               # 导出入口
```

#### 6.2.2 组件模板

```tsx
import React from 'react';
import './ComponentName.css';

interface ComponentNameProps {
  // Props定义
}

export const ComponentName: React.FC<ComponentNameProps> = (props) => {
  // 组件逻辑

  return (
    // JSX结构
  );
};

export default ComponentName;
```

### 6.3 状态管理实现

#### 6.3.1 Context创建模板

```typescript
// 创建Context
import { createContext, useContext, useState, ReactNode } from 'react';

interface ContextValue {
  // 上下文值类型
}

const Context = createContext<ContextValue | undefined>(undefined);

export const ContextProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<any>(null);

  const value: ContextValue = {
    // 上下文值
  };

  return (
    <Context.Provider value={value}>
      {children}
    </Context.Provider>
  );
};

export const useContext = () => {
  const context = useContext(Context);
  if (!context) {
    throw new Error('useContext must be used within ContextProvider');
  }
  return context;
};
```

### 6.4 网络拓扑实现

#### 6.4.1 自定义节点开发

```typescript
import { Handle, Position, NodeProps } from '@xyflow/react';

interface CustomNodeData {
  label: string;
  ip: string;
  status: string;
  warMode: boolean;
  isInStoryline: boolean;
  isSelected: boolean;
}

export const CustomNode: React.FC<NodeProps> = ({ data }) => {
  const { label, ip, status, warMode, isInStoryline, isSelected } = data as CustomNodeData;

  return (
    <div className={`custom-node ${isSelected ? 'selected' : ''}`}>
      <Handle type="target" position={Position.Left} />
      {/* 节点内容 */}
      <Handle type="source" position={Position.Right} />
    </div>
  );
};
```

#### 6.4.2 节点类型注册

```typescript
import { NodeTypes } from '@xyflow/react';
import { ServerNode } from './ServerNode';
import { FirewallNode } from './FirewallNode';
// ... 其他节点导入

export const nodeTypes: NodeTypes = {
  server: ServerNode,
  firewall: FirewallNode,
  // ... 其他节点
};
```

### 6.5 样式编写规范

#### 6.5.1 Tailwind CSS使用规范

- 优先使用Tailwind CSS的utility类
- 自定义样式写在单独的CSS文件中或使用style对象
- 复杂的选择器使用CSS文件
- 响应式设计使用Tailwind的响应式前缀（sm:、md:、lg:等）

#### 6.5.2 颜色使用规范

- 使用语义化的颜色名称（如text-primary、bg-surface）
- 避免直接使用十六进制颜色值
- 在tailwind.config.js中定义项目专用的颜色

---

## 第七章 测试规范

### 7.1 单元测试要求

| 测试类型 | 覆盖要求 | 测试工具 |
|----------|----------|----------|
| 组件渲染测试 | 所有可视化组件 | React Testing Library |
| 交互测试 | 用户交互逻辑 | React Testing Library |
| 状态测试 | 状态更新逻辑 | Jest |

### 7.2 测试示例

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalled();
  });
});
```

---

## 第八章 部署规范

### 8.1 构建配置

生产构建使用Vite执行，输出目录为dist文件夹。构建命令：

```bash
yarn build
```

### 8.2 部署流程

1. 执行生产构建：`yarn build`
2. 将dist目录内容部署到Web服务器
3. 配置SPA路由支持（所有路由回退到index.html）
4. 配置静态资源缓存策略

### 8.3 环境变量

项目使用Vite构建，无需配置特殊环境变量。所有配置通过代码中的常量定义，便于不同环境的切换。

---

## 第九章 验收标准

### 9.1 功能验收

| 功能模块 | 验收条件 | 测试方法 |
|----------|----------|----------|
| 网络拓扑画布 | 正确渲染所有资产节点，支持缩放拖拽 | 手动测试 |
| AI Copilot | 能够发送消息并接收AI回复 | 手动测试 |
| 资产卡片 | 点击节点显示正确的资产信息 | 手动测试 |
| 故事线面板 | 正确显示攻击故事线 | 手动测试 |
| 模式切换 | 和平/战争模式正确切换 | 手动测试 |

### 9.2 视觉验收

| 检查点 | 验收条件 |
|--------|----------|
| 色彩一致性 | 所有界面元素使用设计系统定义的颜色 |
| 响应式布局 | 在1920x1080及以上分辨率正常显示 |
| 动画流畅度 | 动画无卡顿，60fps流畅运行 |
| 可访问性 | 颜色之外有其他视觉区分方式（如图标） |

### 9.3 性能验收

| 指标 | 目标值 |
|------|--------|
| 首次内容渲染（FCP） | <1.5秒 |
| 交互响应时间 | <100毫秒 |
| 内存占用 | <200MB |

---

## 第十章 高级架构与性能优化

### 10.1 状态管理架构（Zustand）

#### 10.1.1 为什么需要Zustand

在网络安全态势感知平台中，告警、节点状态、连线随时都在高频刷新。使用原生React Context会导致整个组件树的无效重渲染（Re-render灾难），这在带有大量SVG渲染的React Flow画布中是致命的。Zustand支持细粒度的状态订阅，能够保证收到高频告警推送时，只更新对应的节点或数字，不触发整个画布重绘。

#### 10.1.2 Zustand Store设计

```typescript
// src/stores/useAppStore.ts
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

interface Alert {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  source_ip: string;
  target_ip: string;
  detected_at: string;
  storyline_id?: string;
  trace_id: string;
}

interface Asset {
  id: string;
  name: string;
  ip: string;
  type: 'server' | 'endpoint' | 'database' | 'firewall' | 'iot' | 'cloud';
  status: 'normal' | 'warning' | 'critical' | 'compromised';
  risk_score: number;
  connections: string[];
}

interface Storyline {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium';
  assets: string[];
  steps: { time: string; event: string; node: string }[];
}

interface AppState {
  // 模式状态
  warMode: boolean;
  setWarMode: (mode: boolean) => void;

  // 资产状态
  assets: Record<string, Asset>;
  setAssets: (assets: Asset[]) => void;
  updateAsset: (id: string, updates: Partial<Asset>) => void;

  // 告警状态
  alerts: Alert[];
  addAlert: (alert: Alert) => void;
  updateAlert: (id: string, updates: Partial<Alert>) => void;
  clearAlerts: () => void;

  // 故事线状态
  storylines: Storyline[];
  selectedStoryline: string | null;
  setSelectedStoryline: (id: string | null) => void;

  // 选中状态
  selectedAsset: string | null;
  setSelectedAsset: (id: string | null) => void;

  // AI Copilot状态
  copilotOpen: boolean;
  setCopilotOpen: (open: boolean) => void;
  currentContext: { type: string; id: string } | null;
  setCurrentContext: (context: { type: string; id: string } | null) => void;

  // 审批任务状态
  pendingApprovals: ApprovalTask[];
  addApproval: (task: ApprovalTask) => void;
  removeApproval: (id: string) => void;
}

interface ApprovalTask {
  id: string;
  type: 'isolate' | 'block_ip' | 'quarantine';
  target: string;
  description: string;
  risk_level: 'high' | 'medium' | 'low';
  requested_by: string;
  requested_at: string;
  trace_id: string;
}

export const useAppStore = create<AppState>()(
  subscribeWithSelector((set) => ({
    // 初始状态
    warMode: false,
    setWarMode: (mode) => set({ warMode: mode }),

    assets: {},
    setAssets: (assets) => set({ assets: assets.reduce((acc, asset) => ({ ...acc, [asset.id]: asset }), {}) }),
    updateAsset: (id, updates) => set((state) => ({
      assets: { ...state.assets, [id]: { ...state.assets[id], ...updates } }
    })),

    alerts: [],
    addAlert: (alert) => set((state) => ({ alerts: [alert, ...state.alerts].slice(0, 1000) })),
    updateAlert: (id, updates) => set((state) => ({
      alerts: state.alerts.map((a) => a.id === id ? { ...a, ...updates } : a)
    })),
    clearAlerts: () => set({ alerts: [] }),

    storylines: [],
    selectedStoryline: null,
    setSelectedStoryline: (id) => set({ selectedStoryline: id }),

    selectedAsset: null,
    setSelectedAsset: (id) => set({ selectedAsset: id }),

    copilotOpen: false,
    setCopilotOpen: (open) => set({ copilotOpen: open }),
    currentContext: null,
    setCurrentContext: (context) => set({ currentContext: context }),

    pendingApprovals: [],
    addApproval: (task) => set((state) => ({ pendingApprovals: [...state.pendingApprovals, task] })),
    removeApproval: (id) => set((state) => ({
      pendingApprovals: state.pendingApprovals.filter((t) => t.id !== id)
    })),
  }))
);

// 细粒度订阅示例
export const useWarMode = () => useAppStore((state) => state.warMode);
export const useSelectedAsset = () => useAppStore((state) => state.selectedAsset);
export const useAlerts = () => useAppStore((state) => state.alerts);
export const usePendingApprovals = () => useAppStore((state) => state.pendingApprovals);
```

#### 10.1.3 依赖注入式使用

```typescript
// 在组件中使用Zustand
import { useAppStore, useWarMode, useSelectedAsset } from '@/stores/useAppStore';

const NetworkCanvas = () => {
  // 只订阅warMode变化，不触发其他组件重渲染
  const warMode = useWarMode();
  const selectedAsset = useSelectedAsset();
  const assets = useAppStore((state) => Object.values(state.assets));

  return (
    <ReactFlow
      nodes={assets.map(asset => ({ ... }))}
      // ...
    />
  );
};
```

### 10.2 实时通信层设计

#### 10.2.1 WebSocket连接管理器

**⚠️ 重要更新**：根据前后端协同核对报告（2026年3月），WebSocket消息类型已与后端完全对齐。使用Socket.io以获得更好的兼容性和重连机制。

```typescript
// src/services/websocket/WebSocketManager.ts
import { io, Socket } from 'socket.io-client';

type MessageHandler = (data: WebSocketMessage) => void;

// 统一的消息类型枚举（与后端完全对齐）
enum WebSocketMessageType {
  // 资产状态更新
  ASSET_STATUS_UPDATE = 'ASSET_STATUS_UPDATE',
  // 人类在环审批请求
  HITL_APPROVAL_REQUIRED = 'HITL_APPROVAL_REQUIRED',
  // 新的告警事件
  NEW_ALERT = 'NEW_ALERT',
  // AI分析进度更新
  ANALYSIS_STAGE_CHANGED = 'ANALYSIS_STAGE_CHANGED',
  // 战时模式触发
  WAR_MODE_TRIGGERED = 'WAR_MODE_TRIGGERED',
  // 新的故事线生成
  NEW_STORYLINE = 'NEW_STORYLINE',
  // 心跳
  HEARTBEAT = 'heartbeat'
}

interface WebSocketMessage {
  type: WebSocketMessageType;
  trace_id: string;
  payload: any;
  timestamp: string;
}

class WebSocketManager {
  private socket: Socket | null = null;
  private url: string;
  private token: string;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: number | null = null;
  private messageQueue: WebSocketMessage[] = [];
  private isConnecting = false;

  constructor(url: string, token: string) {
    this.url = url;
    this.token = token;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.socket?.connected || this.isConnecting) {
        resolve();
        return;
      }

      this.isConnecting = true;

      try {
        // 使用Socket.io替代原生WebSocket
        this.socket = io(this.url, {
          auth: { token: this.token },
          transports: ['websocket', 'polling'],
          reconnection: true,
          reconnectionAttempts: this.maxReconnectAttempts,
          reconnectionDelay: this.reconnectDelay,
        });

        this.socket.on('connect', () => {
          console.log('[Socket.io] Connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.flushMessageQueue();
          resolve();
        });

        this.socket.on('message', (data: string) => {
          try {
            const message: WebSocketMessage = JSON.parse(data);
            this.handleMessage(message);
          } catch (error) {
            console.error('[Socket.io] Parse error:', error);
          }
        });

        this.socket.on('disconnect', (reason) => {
          console.log('[Socket.io] Disconnected:', reason);
          this.isConnecting = false;
          this.stopHeartbeat();
        });

        this.socket.on('connect_error', (error) => {
          console.error('[Socket.io] Connection error:', error);
          this.isConnecting = false;
          reject(error);
        });
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  private handleMessage(message: WebSocketMessage) {
    const handlers = this.handlers.get(message.type);
    if (handlers) {
      handlers.forEach((handler) => handler(message));
    }

    // 同时触发通配符处理器
    const wildcardHandlers = this.handlers.get('*');
    if (wildcardHandlers) {
      wildcardHandlers.forEach((handler) => handler(message));
    }
  }

  subscribe(type: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);

    // 返回取消订阅函数
    return () => {
      this.handlers.get(type)?.delete(handler);
    };
  }

  send(message: Omit<WebSocketMessage, 'timestamp'>) {
    const fullMessage = {
      ...message,
      timestamp: new Date().toISOString(),
    };

    if (this.socket?.connected) {
      this.socket.emit('message', JSON.stringify(fullMessage));
    } else {
      this.messageQueue.push(fullMessage as WebSocketMessage);
    }
  }

  private flushMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send(message);
      }
    }
  }

  private startHeartbeat() {
    this.heartbeatInterval = window.setInterval(() => {
      this.send({
        type: WebSocketMessageType.HEARTBEAT,
        trace_id: '',
        payload: {}
      });
    }, 30000);
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  disconnect() {
    this.stopHeartbeat();
    this.socket?.disconnect();
    this.socket = null;
  }
}

// 导出单例
export const wsManager = new WebSocketManager(
  import.meta.env.VITE_WS_URL || 'wss://api.example.com/ws',
  '' // Token将在认证后设置
);
```

#### 10.2.2 React Hook封装

```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useCallback } from 'react';
import { useAppStore } from '@/stores/useAppStore';
import { wsManager, WebSocketMessage, WebSocketMessageType } from '@/services/websocket/WebSocketManager';

export const useWebSocket = (token: string) => {
  const addAlert = useAppStore((state) => state.addAlert);
  const addApproval = useAppStore((state) => state.addApproval);
  const updateAlert = useAppStore((state) => state.updateAlert);

  useEffect(() => {
    // 设置Token
    (wsManager as any).token = token;

    // 连接Socket.io
    wsManager.connect().catch(console.error);

    // 订阅新的告警消息（与后端对齐）
    const unsubAlert = wsManager.subscribe(WebSocketMessageType.NEW_ALERT, (message: WebSocketMessage) => {
      addAlert(message.payload);
    });

    // 订阅审批任务（与后端对齐）
    const unsubApproval = wsManager.subscribe(WebSocketMessageType.HITL_APPROVAL_REQUIRED, (message: WebSocketMessage) => {
      addApproval(message.payload);
    });

    // 订阅AI分析进度（与后端对齐）
    const unsubProgress = wsManager.subscribe(WebSocketMessageType.ANALYSIS_STAGE_CHANGED, (message: WebSocketMessage) => {
      // 更新AI Copilot进度状态
      console.log('AI Progress:', message.payload);
    });

    // 订阅资产状态更新
    const unsubAssetUpdate = wsManager.subscribe(WebSocketMessageType.ASSET_STATUS_UPDATE, (message: WebSocketMessage) => {
      // 更新资产状态
      console.log('Asset Update:', message.payload);
    });

    return () => {
      unsubAlert();
      unsubApproval();
      unsubProgress();
      unsubAssetUpdate();
      wsManager.disconnect();
    };
  }, [token, addAlert, addApproval, updateAlert]);
};
```

### 10.3 人类在环（HITL）审批工作流

#### 10.3.1 设计理念

后端使用了LangGraph状态机，高危动作会触发拦截（interrupt_before）等待人工审批。前端需要增加「待办审批中心」或「拦截授权面板」。当AI Copilot或后台自动化触发高危操作（如阻断核心交换机端口）时，前端需弹出带有影响面评估的授权卡片，支持用户点击「批准」、「拒绝」或「修改参数后执行」。

#### 10.3.2 审批任务数据模型

```typescript
// src/types/approval.ts
interface ApprovalTask {
  id: string;
  trace_id: string;
  type: ApprovalType;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  target: {
    type: 'asset' | 'ip' | 'network' | 'user';
    id: string;
    name: string;
    description: string;
  };
  action: {
    type: 'isolate' | 'block_ip' | 'quarantine' | 'disable_account' | 'block_domain';
    parameters: Record<string, any>;
  };
  risk_assessment: {
    level: 'critical' | 'high' | 'medium' | 'low';
    impact_scope: string;
    affected_systems: string[];
    business_impact: string;
  };
  requested_by: {
    id: string;
    name: string;
    role: string;
    source: 'ai_copilot' | 'automation' | 'manual';
  };
  requested_at: string;
  expires_at: string;
  approvers: string[];
  approver_comments?: string;
}

type ApprovalType = 'isolate_endpoint' | 'block_ip' | 'block_domain' | 'quarantine_network' | 'suspend_user';
```

#### 10.3.3 审批面板组件

```typescript
// src/components/approval/ApprovalPanel.tsx
import { useState } from 'react';
import { useAppStore, usePendingApprovals } from '@/stores/useAppStore';
import { ShieldAlert, AlertTriangle, X, Check, Edit3 } from 'lucide-react';

export const ApprovalPanel: React.FC = () => {
  const pendingApprovals = usePendingApprovals();
  const removeApproval = useAppStore((state) => state.removeApproval);
  const [selectedTask, setSelectedTask] = useState<string | null>(null);
  const [comment, setComment] = useState('');
  const [modifiedParams, setModifiedParams] = useState<Record<string, any>>({});

  const handleApprove = async (taskId: string) => {
    await fetch(`/api/v1/approvals/${taskId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ comment, modified_params: modifiedParams }),
    });
    removeApproval(taskId);
    setSelectedTask(null);
    setComment('');
    setModifiedParams({});
  };

  const handleReject = async (taskId: string) => {
    await fetch(`/api/v1/approvals/${taskId}/reject`, {
      method: 'POST',
      body: JSON.stringify({ reason: comment }),
    });
    removeApproval(taskId);
    setSelectedTask(null);
    setComment('');
  };

  if (pendingApprovals.length === 0) return null;

  return (
    <div className="fixed right-4 top-20 w-96 max-h-[70vh] overflow-y-auto glass rounded-xl border border-amber-500/30 shadow-2xl z-50">
      <div className="p-4 border-b border-amber-500/30 bg-gradient-to-r from-amber-500/10 to-red-500/10">
        <div className="flex items-center gap-2 text-amber-400">
          <ShieldAlert className="w-5 h-5 animate-pulse" />
          <span className="font-semibold">待审批任务 ({pendingApprovals.length})</span>
        </div>
      </div>

      <div className="p-4 space-y-3">
        {pendingApprovals.map((task) => (
          <div
            key={task.id}
            className={`p-4 rounded-lg border transition-all cursor-pointer ${
              selectedTask === task.id
                ? 'border-amber-500 bg-amber-500/10'
                : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
            }`}
            onClick={() => setSelectedTask(task.id)}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className={`w-4 h-4 ${
                  task.risk_level === 'critical' ? 'text-red-400' : 'text-amber-400'
                }`} />
                <span className="text-sm font-medium text-white">{task.type}</span>
              </div>
              <span className={`text-xs px-2 py-0.5 rounded ${
                task.risk_level === 'critical' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
              }`}>
                {task.risk_level === 'critical' ? '高危' : '风险'}
              </span>
            </div>

            <div className="text-xs text-slate-400 mb-2">{task.description}</div>

            <div className="text-xs text-slate-500">
              影响范围：{task.risk_assessment.impact_scope}
            </div>

            {selectedTask === task.id && (
              <div className="mt-4 space-y-3">
                <div className="p-3 rounded bg-slate-900/50">
                  <div className="text-xs text-slate-500 mb-1">受影响系统</div>
                  <div className="text-sm text-slate-300">
                    {task.risk_assessment.affected_systems.join(', ')}
                  </div>
                </div>

                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="审批意见（可选）"
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500"
                  rows={2}
                />

                <div className="flex gap-2">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleApprove(task.id); }}
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 rounded-lg transition-colors"
                  >
                    <Check className="w-4 h-4" />
                    批准
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleReject(task.id); }}
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4" />
                    拒绝
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 10.4 反馈收集机制（运营即训练）

#### 10.4.1 设计理念

前端设计中缺少对误报/漏报标记的支持，而这是AI持续迭代的灵魂。需要在所有告警和分析界面补充「一键标记误报/漏报」的反馈收集UI组件。

#### 10.4.2 反馈数据模型

```typescript
// src/types/feedback.ts
interface HumanFeedback {
  id: string;
  trace_id: string;
  target_type: 'alert' | 'storyline' | 'copilot_response' | 'analysis';
  target_id: string;
  feedback_type: 'false_positive' | 'true_positive' | 'misclassification' | 'correction' | 'helpful' | 'not_helpful';
  confidence_score?: number;
  category?: string;
  correction?: {
    field: string;
    original_value: string;
    corrected_value: string;
  };
  comment?: string;
  user_id: string;
  created_at: string;
}
```

#### 10.4.3 反馈组件实现

```typescript
// src/components/feedback/FeedbackCollector.tsx
import { useState } from 'react';
import { ThumbsUp, ThumbsDown, Flag, MessageSquare } from 'lucide-react';

interface FeedbackCollectorProps {
  traceId: string;
  targetType: 'alert' | 'storyline' | 'copilot_response';
  targetId: string;
  onFeedbackSubmit?: (feedback: Partial<HumanFeedback>) => void;
}

export const FeedbackCollector: React.FC<FeedbackCollectorProps> = ({
  traceId,
  targetType,
  targetId,
  onFeedbackSubmit,
}) => {
  const [showOptions, setShowOptions] = useState(false);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const feedbackOptions = [
    { value: 'true_positive', label: '👍 正确检测', color: 'text-emerald-400' },
    { value: 'false_positive', label: '👎 误报', color: 'text-red-400' },
    { value: 'misclassification', label: '🔄 分类错误', color: 'text-amber-400' },
    { value: 'helpful', label: '💡 有帮助', color: 'text-cyan-400' },
    { value: 'not_helpful', label: '❌ 无帮助', color: 'text-slate-400' },
  ];

  const handleSubmit = async () => {
    const feedback = {
      trace_id: traceId,
      target_type: targetType,
      target_id: targetId,
      feedback_type: selectedOption as any,
      comment: comment || undefined,
      created_at: new Date().toISOString(),
    };

    await fetch('/api/v1/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(feedback),
    });

    setSubmitted(true);
    onFeedbackSubmit?.(feedback);
  };

  if (submitted) {
    return (
      <div className="text-xs text-emerald-400 flex items-center gap-1">
        <ThumbsUp className="w-3 h-3" />
        已收到反馈
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {!showOptions ? (
        <div className="flex items-center gap-1">
          <button
            onClick={() => setShowOptions(true)}
            className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
            title="提供反馈"
          >
            <Flag className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div className="flex flex-col gap-2 p-2 bg-slate-800 rounded-lg border border-slate-700">
          <div className="flex flex-wrap gap-1">
            {feedbackOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setSelectedOption(option.value)}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  selectedOption === option.value
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-400 hover:bg-slate-700'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>

          {selectedOption && (
            <>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="补充说明（可选）"
                className="px-2 py-1 bg-slate-900 border border-slate-700 rounded text-xs text-white placeholder-slate-500"
                rows={2}
              />

              <div className="flex gap-2">
                <button
                  onClick={handleSubmit}
                  className="flex-1 px-2 py-1 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 rounded text-xs"
                >
                  提交
                </button>
                <button
                  onClick={() => { setShowOptions(false); setSelectedOption(null); }}
                  className="px-2 py-1 text-slate-400 hover:text-white rounded text-xs"
                >
                  取消
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};
```

### 10.5 角色-based访问控制与多视图路由

#### 10.5.1 设计理念

真实的SOC有明确的职能划分。前端需要补充路由设计体系，不同角色默认进入不同视图。

| 角色 | 默认视图 | 核心功能 |
|------|----------|----------|
| Tier 1（值班监控） | 大屏画布 | 高频告警流、实时态势 |
| Tier 2/3（深度研判） | 调查工作台 | 调查图谱、日志检索 |
| 管理层（CISO） | 合规报表 | SLA统计、合规大盘 |

#### 10.5.2 路由配置

```typescript
// src/router/AppRoutes.tsx
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { useAppStore } from '@/stores/useAppStore';

const DashboardLayout = React.lazy(() => import('@/pages/Dashboard'));
const InvestigationLayout = React.lazy(() => import('@/pages/Investigation'));
const ReportsLayout = React.lazy(() => import('@/pages/Reports'));
const SettingsPage = React.lazy(() => import('@/pages/Settings'));

interface RoleConfig {
  defaultRoute: string;
  allowedRoutes: string[];
}

const roleConfigs: Record<string, RoleConfig> = {
  admin: {
    defaultRoute: '/dashboard',
    allowedRoutes: ['/dashboard', '/investigation', '/reports', '/settings', '/admin'],
  },
  senior_analyst: {
    defaultRoute: '/investigation',
    allowedRoutes: ['/dashboard', '/investigation', '/reports'],
  },
  analyst: {
    defaultRoute: '/dashboard',
    allowedRoutes: ['/dashboard', '/investigation'],
  },
  viewer: {
    defaultRoute: '/dashboard',
    allowedRoutes: ['/dashboard', '/reports'],
  },
};

const ProtectedRoute: React.FC<{ children: React.ReactNode; allowedRoutes: string[] }> = ({
  children,
  allowedRoutes,
}) => {
  const currentPath = window.location.pathname;
  const userRole = useAppStore.getState().user?.role || 'viewer';

  if (!allowedRoutes.includes(currentPath)) {
    return <Navigate to={roleConfigs[userRole]?.defaultRoute || '/dashboard'} replace />;
  }

  return <>{children}</>;
};

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to={roleConfigs[useAppStore.getState().user?.role || 'analyst']?.defaultRoute || '/dashboard'} replace />,
  },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute allowedRoutes={roleConfigs[useAppStore.getState().user?.role || 'analyst']?.allowedRoutes || []}>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <NetworkCanvasPage /> },
      { path: 'alerts', element: <AlertStreamPage /> },
      { path: 'assets', element: <AssetListPage /> },
    ],
  },
  {
    path: '/investigation',
    element: (
      <ProtectedRoute allowedRoutes={roleConfigs[useAppStore.getState().user?.role || 'analyst']?.allowedRoutes || []}>
        <InvestigationLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <InvestigationDashboard /> },
      { path: ':incidentId', element: <IncidentDetail /> },
      { path: 'graph', element: <AttackGraphPage /> },
      { path: 'logs', element: <LogSearchPage /> },
    ],
  },
  {
    path: '/reports',
    element: (
      <ProtectedRoute allowedRoutes={roleConfigs[useAppStore.getState().user?.role || 'analyst']?.allowedRoutes || []}>
        <ReportsLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <ComplianceDashboard /> },
      { path: 'sla', element: <SLAPage /> },
      { path: 'trends', element: <TrendsPage /> },
    ],
  },
]);
```

### 10.6 分布式追踪与AI推理链可视化

#### 10.6.1 trace_id贯穿设计

在分布式和AI代理链中，必须有一个贯穿始终的trace_id。前端所有的模型（告警、故事线、甚至聊天消息）都必须增加trace_id字段，以便在点击反馈或执行动作时，能够精准追溯后端的原始事件。

```typescript
// 更新数据模型，添加trace_id
interface Alert {
  id: string;
  trace_id: string;  // 必填字段
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  source_ip: string;
  target_ip: string;
  detected_at: string;
  storyline_id?: string;
}

interface Storyline {
  id: string;
  trace_id: string;  // 必填字段
  title: string;
  severity: 'critical' | 'high' | 'medium';
  assets: string[];
  steps: { time: string; event: string; node: string }[];
}

interface ChatMessage {
  id: string;
  trace_id: string;  // 必填字段，用于追踪对话上下文
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  actions?: { label: string; action: string }[];
}
```

#### 10.6.2 AI推理链可视化

后端AI分析会输出mitre_tactics、mitre_techniques以及analysis_reasoning（置信度与推理过程）。前端需要在UI中采用如「折叠面板」或「思维链进度条」的方式，把AI的思考过程透明地展示给分析师。

```typescript
// src/components/copilot/AnalysisReasoning.tsx
import { useState } from 'react';
import { ChevronDown, ChevronRight, Brain, Target, AlertTriangle } from 'lucide-react';

interface ReasoningStep {
  id: string;
  step: number;
  thought: string;
  evidence: string[];
  confidence: number;
  mitre_tactic?: string;
  mitre_technique?: string;
}

interface AnalysisReasoningProps {
  reasoning: ReasoningStep[];
  overall_confidence: number;
}

export const AnalysisReasoning: React.FC<AnalysisReasoningProps> = ({
  reasoning,
  overall_confidence,
}) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="mt-4 border border-slate-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-3 bg-slate-800/50 hover:bg-slate-800 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-cyan-400" />
          <span className="text-sm text-white">AI分析推理链</span>
          <span className={`text-xs px-2 py-0.5 rounded ${
            overall_confidence >= 80 ? 'bg-emerald-500/20 text-emerald-400' :
            overall_confidence >= 60 ? 'bg-amber-500/20 text-amber-400' :
            'bg-red-500/20 text-red-400'
          }`}>
            置信度 {overall_confidence}%
          </span>
        </div>
        {expanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
      </button>

      {expanded && (
        <div className="p-3 space-y-2 bg-slate-900/50">
          {reasoning.map((step, index) => (
            <div key={step.id} className="flex gap-3">
              <div className="flex flex-col items-center">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                  step.confidence >= 80 ? 'bg-emerald-500/20 text-emerald-400' :
                  step.confidence >= 60 ? 'bg-amber-500/20 text-amber-400' :
                  'bg-red-500/20 text-red-400'
                }`}>
                  {index + 1}
                </div>
                {index < reasoning.length - 1 && (
                  <div className="w-px h-full bg-slate-700 my-1" />
                )}
              </div>

              <div className="flex-1 pb-3">
                <div className="text-sm text-white mb-1">{step.thought}</div>
                <div className="flex items-center gap-2 mb-2">
                  {step.mitre_tactic && (
                    <span className="text-xs px-2 py-0.5 bg-red-500/20 text-red-400 rounded">
                      {step.mitre_tactic}
                    </span>
                  )}
                  {step.mitre_technique && (
                    <span className="text-xs px-2 py-0.5 bg-orange-500/20 text-orange-400 rounded">
                      {step.mitre_technique}
                    </span>
                  )}
                  <span className="text-xs text-slate-500">
                    置信度 {step.confidence}%
                  </span>
                </div>

                {step.evidence.length > 0 && (
                  <div className="text-xs text-slate-400 space-y-1">
                    {step.evidence.map((ev, i) => (
                      <div key={i} className="flex items-start gap-1">
                        <AlertTriangle className="w-3 h-3 text-slate-500 mt-0.5" />
                        <span>{ev}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

### 10.7 拓扑图海量节点优化

#### 10.7.1 节点聚合策略

企业网络可能有几万到几十万个资产节点。如果在React Flow中一次性渲染超过2000个节点，前端会卡死。需要补充「拓扑节点聚合（Clustering）」的设计。在宏观缩放级别（Zoom Out）时，将节点按部门、子网或设备类型聚合为一个「超级节点（群组）」；只有当用户双击或拉近视角（Zoom In）时，才展开显示具体的IP节点。

#### 10.7.2 聚合算法实现

```typescript
// src/components/network/NodeClustering.tsx
import { useMemo, useCallback } from 'react';
import { useViewport, useNodesState, useEdgesState } from '@xyflow/react';

interface ClusterConfig {
  group_by: 'department' | 'subnet' | 'type' | 'risk_level';
  zoom_threshold: {
    cluster: number;  // 小于此缩放级别时聚合
    expand: number;   // 大于此缩放级别时展开
  };
}

export const useNodeClustering = (
  assets: Asset[],
  config: ClusterConfig
) => {
  const [viewport] = useViewport();

  // 根据缩放级别判断是否聚合
  const shouldCluster = useMemo(() => {
    return viewport.zoom < config.zoom_threshold.cluster;
  }, [viewport.zoom, config.zoom_threshold.cluster]);

  // 聚合节点
  const clusteredNodes = useMemo(() => {
    if (!shouldCluster) {
      return assets.map((asset) => ({
        id: asset.id,
        type: asset.type,
        position: { x: 0, y: 0 }, // 实际位置由布局算法计算
        data: { ...asset, isClustered: false },
      }));
    }

    // 按配置字段分组
    const groups = assets.reduce((acc, asset) => {
      const key = asset[config.group_by] || 'unknown';
      if (!acc[key]) {
        acc[key] = [];
      }
      acc[key].push(asset);
      return acc;
    }, {} as Record<string, Asset[]>);

    // 创建聚合节点
    return Object.entries(groups).map(([key, groupAssets]) => ({
      id: `cluster-${key}`,
      type: 'cluster',
      position: calculateClusterPosition(groupAssets), // 计算群组中心位置
      data: {
        label: key,
        group_by: config.group_by,
        asset_count: groupAssets.length,
        critical_count: groupAssets.filter((a) => a.status === 'critical' || a.status === 'compromised')..length,
        warning_count: groupAssets.filter((a) => a.status === 'warning').length,
        assets: groupAssets,
        isClustered: true,
      },
    }));
  }, [assets, shouldCluster, config]);

  // 展开聚合节点
  const expandCluster = useCallback((clusterId: string) => {
    // 当用户双击聚合节点时，切换到展开视图
    // 实际实现需要在NetworkCanvas中处理
  }, []);

  return {
    nodes: clusteredNodes,
    shouldCluster,
    expandCluster,
  };
};

// 计算群组中心位置（简化版，实际需要更复杂的布局算法）
const calculateClusterPosition = (assets: Asset[]): { x: number; y: number } => {
  if (assets.length === 0) return { x: 0, y: 0 };

  // 按子网分组计算
  const subnets = assets.reduce((acc, asset) => {
    const subnet = asset.ip.split('.').slice(0, 2).join('.');
    if (!acc[subnet]) acc[subnet] = [];
    acc[subnet].push(asset);
    return acc;
  }, {} as Record<string, Asset[]>);

  const subnetEntries = Object.entries(subnets);
  const index = subnetEntries.findIndex(([key]) =>
    assets.some((a) => a.ip.startsWith(key))
  );

  const angle = (index / Math.max(subnetEntries.length, 1)) * 2 * Math.PI;
  const radius = 300;

  return {
    x: 400 + radius * Math.cos(angle),
    y: 300 + radius * Math.sin(angle),
  };
};
```

#### 10.7.3 聚合节点组件

```typescript
// src/components/network/nodes/ClusterNode.tsx
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Layers, Server, Shield, Database } from 'lucide-react';

interface ClusterNodeData {
  label: string;
  group_by: string;
  asset_count: number;
  critical_count: number;
  warning_count: number;
  assets: Asset[];
  warMode: boolean;
}

export const ClusterNode: React.FC<NodeProps> = ({ data }) => {
  const { label, asset_count, critical_count, warning_count, warMode, isSelected } = data as ClusterNodeData;

  const getIcon = () => {
    switch (data.group_by) {
      case 'type': return <Server className="w-5 h-5" />;
      case 'department': return <Layers className="w-5 h-5" />;
      default: return <Database className="w-5 h-5" />;
    }
  };

  return (
    <div className={`relative px-4 py-3 rounded-xl border-2 transition-all min-w-[180px] ${
      isSelected
        ? warMode ? 'border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.6)]' : 'border-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.6)]'
        : warMode ? 'border-red-500/50' : 'border-slate-600'
    } ${warMode ? 'bg-red-500/10' : 'bg-slate-900'}`}>
      <Handle type="target" position={Position.Left} className="!bg-slate-500 !w-3 !h-3" />

      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
          critical_count > 0
            ? warMode ? 'bg-red-500/30' : 'bg-red-500/20'
            : warning_count > 0
              ? 'bg-amber-500/20'
              : 'bg-cyan-500/20'
        }`}>
          {getIcon()}
        </div>
        <div>
          <div className="text-sm font-medium text-white">{label}</div>
          <div className="text-xs text-slate-400">
            {asset_count} 个资产
          </div>
        </div>
      </div>

      {/* 状态指示 */}
      <div className="absolute -top-1 -right-1 flex gap-1">
        {critical_count > 0 && (
          <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center text-[10px] text-white font-bold">
            {critical_count}
          </div>
        )}
        {warning_count > 0 && (
          <div className="w-5 h-5 rounded-full bg-amber-500 flex items-center justify-center text-[10px] text-white font-bold">
            {warning_count}
          </div>
        )}
      </div>

      <Handle type="source" position={Position.Right} className="!bg-slate-500 !w-3 !h-3" />
    </div>
  );
};
```

---

## 第十一章 前后端共享数据模型Schema策略

### 11.1 统一建模原则

根据前后端协同核对报告（2026年3月），为确保前后端数据模型的一致性，采用以下建模原则：

| 原则 | 描述 |
|------|------|
| **单一真相源（SSOT）** | 后端Pydantic模型作为唯一真实数据源，前端TypeScript接口从中自动生成 |
| **命名规范统一** | 所有JSON传输字段使用snake_case，前端TypeScript内部变量使用camelCase但API层必须支持snake_case转换 |
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

### 11.3 WebSocket消息类型对齐

根据核对报告，前端WebSocket消息类型已与后端完全对齐：

| 后端消息类型 | 前端枚举值 | 说明 |
|-------------|-----------|------|
| `ASSET_STATUS_UPDATE` | `WebSocketMessageType.ASSET_STATUS_UPDATE` | 资产状态更新 |
| `HITL_APPROVAL_REQUIRED` | `WebSocketMessageType.HITL_APPROVAL_REQUIRED` | 人类在环审批请求 |
| `NEW_ALERT` | `WebSocketMessageType.NEW_ALERT` | 新的告警事件 |
| `ANALYSIS_STAGE_CHANGED` | `WebSocketMessageType.ANALYSIS_STAGE_CHANGED` | AI分析进度更新 |
| `WAR_MODE_TRIGGERED` | `WebSocketMessageType.WAR_MODE_TRIGGERED` | 战时模式触发 |
| `NEW_STORYLINE` | `WebSocketMessageType.NEW_STORYLINE` | 新的故事线生成 |

---

## 附录A：关键文件清单

| 文件路径 | 说明 |
|----------|------|
| /src/App.tsx | 主应用组件，包含所有核心状态和组件组合 |
| /src/main.tsx | 应用入口文件 |
| /src/index.css | 全局样式文件，包含Tailwind指令和自定义样式 |
| /package.json | 项目依赖配置 |
| /tailwind.config.js | Tailwind CSS配置 |
| /vite.config.ts | Vite构建配置 |
| /tsconfig.json | TypeScript配置 |
| /SPEC.md | 项目规格说明书 |

---

## 附录B：依赖版本参考

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.294.0",
    "recharts": "^2.10.3",
    "@xyflow/react": "^12.0.0",
    "socket.io-client": "^4.7.0",
    "zustand": "^4.4.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
```

---

*本文档版本：v1.1.0 (协同修复版)*
*最后更新：2026年3月14日*