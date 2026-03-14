# 企业级 AI-SecOps 项目开发 Harness Engineering 最佳实践指南

## 文档概述

OpenClaw 项目开发遵循 Claude Code 开发规范。

本文档旨在为使用 OpenClaw 开发企业级 AI-SecOps（智能安全运营）项目提供全面的 Harness Engineering 最佳实践指导。AI-SecOps 项目具有高度的复杂性，涉及多层级架构、异构数据源集成、大规模 Agent 编排、前端交互界面开发以及严格的安全合规要求，传统的开发方法难以应对这些挑战。Harness Engineering 作为一种新兴的工程学科，强调通过设计系统化的约束条件、反馈循环和生命周期管理机制，使 AI 编码代理能够可靠地完成复杂的企业级开发任务。

AI-SecOps 项目的核心目标是解决企业网络安全运营面临的困境，通过结合大语言模型（LLM）和智能算法能力，构建下一代智能网络安全运维系统。



该系统的关键能力包括三个核心维度：

第一，后台实时分析威胁并生成防御策略、自动响应处理与协同联防；

第二，前台（React）提供与真人运维人员的自然语言交互界面，使运维人员能够通过对话方式完成安全运营任务；

第三，收集运维人员的操作反馈为系统迭代和优化提供数据支持，形成持续改进的闭环。

这是一个复杂的系统工程，需要精心设计的架构和工程实践来确保系统的可靠性和可维护性。



本文档的核心目标是将 OpenClaw 的 Harness Engineering 理论与 AI-SecOps 项目的具体实践相结合，为开发团队提供一套可落地的工程方法论。文档内容涵盖上下文工程、架构约束、熵管理、测试框架、长期运行 Agent 管理、前端开发实践、反馈收集机制以及安全考虑等核心主题，并结合 AI-SecOps 项目的九层架构体系给出具体的设计建议和实施指南。

本指南假定开发团队已具备基本的 OpenClaw 使用经验，熟悉 Python（3.12.8）编程语言和 React 前端开发技术，了解网络安全领域的基本概念，并能够在 Ubuntu 22.04 环境中进行开发工作。文档中的建议并非一成不变的强制性规范，而是经过验证的有效模式，团队应根据自身实际情况进行调整和优化。

---

## 第一部分：AI-SecOps 项目概述与网络安全运营挑战分析

### 1.1 企业级网络安全运营的现实困境

在当今数字化转型的浪潮中，企业网络安全运营中心（SOC）面临着前所未有的运营压力。现代企业网络中部署了大量异构的安全设备，包括终端检测与响应（EDR）系统、网络流量分析（NTA）平台、各类下一代防火墙（NGFW）和入侵检测/防御系统（IDS/IPS）等。这些安全设备每天产生海量的安全告警——一个中型企业的SOC每天可能需要处理数万甚至数十万条告警，而安全分析师的人力和精力却是有限的。

当前网络安全运营的核心困境体现在以下几个方面：

**告警疲劳与人力瓶颈**：SOC分析师每天被海量告警淹没，其中90%以上的告警是误报或低优先级事件。分析师需要在众多告警中手动筛选出真正的威胁，这种低效的人工分析模式导致真实的攻击往往被淹没在噪音中。

**数据孤岛与碎片化管理**：不同厂商的安全设备使用各自的私有数据格式，终端行为日志、网络流量数据、防火墙告警、EDR事件之间缺乏统一标准。安全分析师难以快速关联跨设备的攻击线索，无法形成完整的攻击链路视图。

**响应滞后与协同困难**：从威胁发现到响应处置的链路冗长，涉及多个安全工具和人工审批环节。缺乏自动化的响应编排能力，导致面对高级持续性威胁（APT）时，攻击者早已完成横向移动甚至数据窃取，SOC才能做出反应。

**知识流失与能力断层**：资深安全分析师的分析经验和处置逻辑难以沉淀和复用，新手分析师的培养周期长，导致SOC整体分析能力的提升缓慢。

AI-SecOps（智能安全运营）项目正是为解决上述网络安全运营困境而生。通过将大语言模型（LLM）与智能算法深度融入SOC工作流程，构建下一代智能安全运营平台，实现从"被动响应"到"主动防御"、从"人工分析"到"智能研判"、从"单点处置"到"协同联防"的范式转变。

### 1.2 AI-SecOps 系统的三层安全运营能力架构

AI-SecOps 系统从安全运营工作流的视角，可以划分为三个紧密协作的能力层次，分别对应 SOC 运营中的**智能分析**、**人机协同**和**持续改进**三大核心环节。

**后台智能分析层（Security Intelligence Layer）**是 SOC 的智能大脑，承担 7×24 小时不间断的威胁监测与分析任务。该层直接对接企业现有的安全基础设施（SIEM、EDR、NDR、防火墙等），实时摄取海量安全事件数据，通过 AI 算法进行自动化威胁研判。具体运营价值包括：
- **告警降噪**：将每日数万条原始告警智能筛选为数十条高价值安全事件，消除告警疲劳
- **深度分析**：运用 LLM 进行攻击意图识别、战术技术映射（MITRE ATT&CK）和影响面评估
- **自动响应**：对低风险事件自动执行预定义处置 playbook，对高风险事件生成包含详细上下文的处置建议
- **知识沉淀**：将每次分析过程和结论结构化存储，形成可检索、可复用的安全知识库

技术实现上，后台层采用九层架构设计，集成 DSPy（智能分析）、Neo4j（攻击图谱）、LangGraph（响应编排）、AutoGen（对抗推演）等框架，构建端到端的智能安全运营流水线。

**前台人机协同层（Security Operations Interface）**是 SOC 分析师与 AI 系统交互的统一入口，采用 React 技术栈构建。传统的 SOC 工具界面复杂、学习成本高，而 AI-SecOps 的前台通过自然语言交互大幅降低使用门槛，使初级分析师也能像资深专家一样高效工作。核心运营场景包括：
- **自然语言查询**：分析师用中文提问"最近三天有哪些横向移动迹象"，系统自动转换为图谱查询并呈现结果
- **智能事件研判**：系统自动生成的威胁分析报告，分析师可一键确认、修改或补充，形成人机协作闭环
- **响应决策支持**：高风险处置操作（如隔离核心业务主机）通过可视化界面展示风险影响，支持一键审批或调整
- **实时态势感知**：动态更新的安全态势仪表板，帮助运营主管快速掌握企业整体安全状态

**反馈优化层（Continuous Improvement Engine）**是保障 SOC 运营能力持续进化的关键机制。传统 SOC 的规则和模型更新周期长、滞后于威胁态势，而 AI-SecOps 通过实时收集一线分析师的反馈，实现"运营即训练"的敏捷迭代。反馈数据直接驱动：
- **检测模型优化**：分析师标记的误报/漏报自动回流训练数据，持续改进 AI 研判准确率
- **响应策略调整**：根据分析师对处置建议的采纳率，优化自动化响应的置信度阈值
- **知识库更新**：分析师补充的攻击上下文和 IOC 情报，自动 enrich 到知识图谱
- **个性化推荐**：学习不同分析师的操作偏好，提供个性化的界面布局和分析视角

### 1.3 AI-SecOps 九层安全运营技术架构

AI-SecOps 九层架构体系是支撑现代 SOC 运营的技术底座，每层对应安全运营工作流中的关键环节，共同实现从数据采集到决策执行的端到端自动化。以下详述各层在 SOC 运营中的具体职责和价值：

**第1层：防洪网关层（Alert Flood Control）**—— SOC 告警降噪的第一道防线
面对每日涌入的数十万条原始安全告警，SOC 分析师不可能逐条审查。防洪网关层通过高性能规则引擎实现毫秒级告警筛选，仅将高置信度威胁事件推送给下游分析。运营价值：将分析师从告警海洋中解放出来，专注处理真正需要人工研判的高价值事件。技术实现：采用 Sigma 规则引擎，通过倒排索引和 Aho-Corasick 算法实现 O(1) 复杂度的规则匹配，过滤效率达到每秒处理 10 万+ 事件。

**第2层：数据清洗与标准化层（Data Normalization）**—— 统一 SOC 数据语言
企业网络中防火墙、EDR、IDS 等设备产生的日志格式各异，传统 SOC 需要分析师记忆数十种不同的日志格式。该层使用 DSPy 驱动的智能提取引擎，将异构日志自动映射为 OCSF 标准格式，实现跨设备的数据统一。运营价值：分析师无需关注底层设备差异，使用统一的数据视图进行分析；新设备接入 SOC 时无需修改分析逻辑，降低集成成本。

**第3层：数据关联与知识图谱层（Threat Correlation）**—— 发现隐蔽攻击链路
单一设备告警往往只能看到攻击的片段，难以识别 APT 攻击的完整杀伤链。该层基于 Neo4j 构建安全知识图谱，将 IP、域名、文件哈希、用户账号等实体关联为攻击图谱。运营价值：自动发现传统 SIEM 规则难以检测的横向移动、权限提升等隐蔽行为；支持一键溯源，快速定位攻击入口和受影响资产。

**第4层：信息聚合与压缩层（Context Compression）**—— 为分析师提供决策精华
攻击事件往往涉及数百个关联实体和数千条相关日志，直接呈现给分析师会导致信息过载。该层使用时序聚合和图嵌入技术，将爆炸式的关联数据压缩为高信息密度的"事件摘要"。运营价值：分析师在 30 秒内即可掌握事件全貌，而非花费数小时翻阅原始日志；LLM 分析层也能在有限上下文窗口内处理更多事件。

**第5层：智能威胁分析层（AI-Powered Analysis）**—— 7×24 小时虚拟安全专家
这是 SOC 的"虚拟 Tier-3 分析师"，使用 DSPy 框架驱动的 AI Agent 对事件进行深度研判。不仅判断"是否恶意"，还能输出 MITRE ATT&CK 战术技术映射、攻击者意图推断、业务影响评估和具体处置建议。运营价值：初级分析师也能获得专家级的分析支撑；分析结论标准化、可审计，避免人工分析的随意性。

**第6层：控制中枢与编排层（Response Orchestration）**—— 安全运营的工作流引擎
该层基于 LangGraph 实现工业级状态机，将分析结论转化为可执行的响应动作序列（遵循标准化的 OpenC2 协议）。内置人类在环（HITL）机制，对不同风险等级的操作设置差异化的审批流程。运营价值：低风险事件（如隔离测试环境主机）可自动执行，秒级响应；高风险事件（如阻断核心业务流量）必须经人工确认，平衡效率与安全。

**第7层：深度对抗与溯源推演层（Adversarial Simulation）**—— 主动防御的"红蓝对抗"
面对未知高级威胁，该层使用 AutoGen 多 Agent 系统模拟攻击者视角，推演"如果我是攻击者，下一步会做什么"，预测潜在攻击路径。运营价值：从被动响应转向主动防御，提前加固可能的攻击跳板；为分析师提供"假设分析"能力，评估不同响应策略的潜在后果。

**第8层：终端执行层（Endpoint Execution）**—— 安全决策的"最后一公里"
该层通过在终端上安装 pi-mono 框架构建的类似于 OpenClaw 那种可以控制操作系统的智能代理，接收来自控制中枢与编排层的标准 OpenC2 指令，在受控的沙盒环境中执行指令。运营价值：打通分析与处置的断层，实现"检测-分析-决策-响应"的闭环；标准化的 OpenC2 协议确保指令可跨厂商设备统一执行。

**第9层：复盘与研报层（Reporting & Compliance）**—— 安全运营的价值呈现
自动将技术事件转化为管理层可读的安全报告，包含攻击时间线、影响范围、处置过程和改进建议。支持合规场景的自动报告生成（如等保、ISO27001）。运营价值：将 SOC 的技术工作转化为可视化的安全价值，提升安全团队的话语权；自动化合规报告节省大量人工文档工作。

### 1.4 开发过程中的核心挑战

AI-SecOps 项目的开发面临着多重挑战，这些挑战贯穿于整个开发生命周期，需要通过系统化的 Harness Engineering 方法来应对。

**多层级架构的复杂性**是首要挑战。九层架构涉及多种技术栈的集成，包括流处理引擎（DSPy）、图数据库（Neo4j）、状态机编排（LangGraph）、多 Agent 系统（AutoGen、CrewAI）以及前端框架（React）等。如何确保各层之间的接口清晰、交互可靠，是系统能否正常工作的关键。

**前后端协同的复杂性**是第二重挑战。后台智能分析能力和前台交互界面需要紧密配合，前端需要准确展示后台的分析结果，后台需要接收来自前端的用户反馈。前后端的数据格式定义、API 设计、WebSocket 通信机制等都需要精心设计。

**数据质量的不确定性**是第三重挑战。企业环境的异构日志格式千奇百怪，即使经过规则引擎的初步过滤，仍可能包含大量噪声和异常数据。如何设计有效的验证和纠错机制，确保分析层获得高质量的输入，是开发过程中需要持续关注的问题。

**长期运行的可靠性**是第四重挑战。AI-SecOps 系统需要全天候运行，处理持续流入的安全事件。OpenClaw 等 AI 编程代理在离散会话中工作，会话之间没有记忆，如何确保多个会话之间的状态连续性和工作协调性，是一个需要专门设计的工程问题。

**安全合规的严格性**是第五重挑战。安全运营系统本身必须满足极高的安全要求，特别是涉及自动化响应的功能，任何错误都可能导致业务中断甚至安全事故。如何在追求自动化的同时保持可控性，是系统设计的核心考量。

---

## 第二部分：Harness Engineering 核心原则在 AI-SecOps 中的应用

### 2.1 约束机制的建立

Harness Engineering 的核心原则之一是通过约束机制来引导 AI 代理的行为，使其在正确的方向上工作。对于 AI-SecOps 项目而言，约束机制的建立尤为重要，因为系统的每个组件都有明确的职责边界和交互接口。

**架构边界的强制约束**是首要任务。在 AI-SecOps 九层架构中，每一层都有明确的输入输出规范。以数据清洗与提取层为例，该层必须输出符合 OCSF 标准格式的结构化数据，任何偏离该约束的输出都应该被标记为错误并触发重试机制。这种约束可以通过 Pydantic 模型的强制校验来实现，当模型输出的 JSON 缺少必要字段或类型不符时，系统自动拒绝并要求重新生成。

**前后端交互的约束**同样关键。前端 React 应用与后端 API 之间的交互应当遵循严格的接口契约。前端只能通过定义好的 API 端点与后端通信，后端返回的数据格式必须符合预定义的 TypeScript 接口或 Pydantic 模型。这种约束可以通过 OpenAPI 规范和 TypeScript 类型定义来实现，确保前后端的数据交换始终保持一致。

**依赖方向的层级约束**同样关键。参考依赖分层的原则，AI-SecOps 架构应当遵循**类型定义 → 数据模型 → 核心逻辑 → 编排控制 → 终端执行**的单向依赖关系。这种约束可以通过自定义的 linter 规则来强制执行，例如禁止上层模块直接调用下层模块的内部 API，只能通过定义好的接口进行交互。

**安全操作的执行约束**是 AI-SecOps 的特殊需求。终端执行层的所有操作都必须经过严格的验证，确保不会产生破坏性的后果。OpenC2 标准提供了规范化的指令格式，应当作为唯一的执行入口。任何试图绕过标准接口直接执行系统命令的操作都应当被禁止。

### 2.2 上下文工程的应用

上下文工程确保 AI 代理在正确的时间拥有正确的信息。在 AI-SecOps 项目中，上下文工程需要考虑多个维度的信息需求。

**静态上下文的定义**应当覆盖项目的所有关键方面。开发团队应当在项目根目录创建 `AI_SECOPS.md` 文件（类似于 OpenClaw 的 `CLAUDE.md`），记录以下核心信息：

项目架构部分应当详细描述九层架构的整体设计，包括每一层的职责、核心模块的划分以及模块之间的交互接口。前端架构部分应当描述 React 应用的整体结构、组件层次、状态管理方案以及与后端的交互方式。数据规范部分应当明确所有使用的数据标准，包括 OCSF 格式的字段定义、STIX 2.1 对象的映射规则、TypeScript 接口定义以及内部定义的扩展字段。编码约定部分应当规定 Python 异步编程的风格、Pydantic 模型的使用规范、React 组件的开发规范、TypeScript 类型定义规则等。运维指南部分应当记录常见的部署场景、配置参数的意义以及故障排查的基本步骤。

**动态上下文的获取**需要在代理运行时提供实时的状态信息。OpenClaw 在每次会话开始时，应当能够获取以下动态上下文：CI/CD 管道的当前状态，包括构建和测试的最近执行结果；开发服务器的运行状态，确保能够正常启动和调试；代码库的 git 历史，包括最近的提交和分支状态；前端构建的状态，包括 TypeScript 类型检查和 linting 结果；当前会话的进度文件，记录本次会话计划完成的任务。

**关键文件模板**是上下文工程的重要组成部分。AI-SecOps 项目应当预定义以下关键文件模板，供 OpenClaw 在开发过程中使用：

`init.sh` 脚本应当包含启动完整开发环境的所有命令，包括后端微服务的启动顺序、前端开发服务器的启动命令、依赖服务的检查逻辑以及健康检查的端点。

`features.json` 文件应当列出所有需要实现的功能点，包括功能描述、验收标准、测试步骤和优先级。每个功能应当有明确的完成标准，OpenClaw 只能将功能标记为通过，经过实际测试验证之后才能标记。

`progress.md` 文件应当记录开发的进度，包括已完成的功能、当前正在处理的任务以及遇到的问题和解决方案。

### 2.3 反馈循环的设计

反馈循环是确保 AI 代理持续改进和自我修正的关键机制。在 AI-SecOps 项目中，反馈循环应当覆盖多个层面。

**开发阶段的即时反馈机制**通过自动化测试和验证实现。每次 OpenClaw 完成代码修改后，系统应当自动运行单元测试、集成测试和代码质量检查。如果测试失败，代理应当立即收到反馈并尝试修复。这种即时反馈可以防止错误的累积，提高代码质量。

**开发阶段的阶段性反馈机制**通过功能验证实现。在实现每个功能点时，OpenClaw 应当按照 `features.json` 中定义的测试步骤进行验证，只有通过验证后才能标记功能为完成。阶段性反馈有助于确保每个功能都达到预期的质量标准。

**运行阶段的用户反馈机制**通过前端界面实现。系统应当提供便捷的反馈收集界面，使运维人员能够轻松标记误报、漏报和提供改进建议。反馈数据应当结构化存储，便于后续分析和处理。

**运行阶段的数据分析机制**通过定期分析实现。系统应当定期分析收集到的反馈数据，识别系统性能的瓶颈和改进方向。分析结果应当用于指导后续的模型优化和功能改进。

### 2.4 熵管理的实施

熵管理解决 AI 生成的代码库随时间积累的 drift 问题。对于 AI-SecOps 项目而言，熵管理尤为重要，因为系统需要长期维护，而多次由 AI 生成的代码可能导致不一致性。

**文档一致性代理**应当定期运行，验证代码实现与文档描述的一致性。AI-SecOps 项目的技术文档应当与代码保持同步，任何代码修改都应当触发文档更新检查。

**架构合规检查代理**应当定期扫描代码库，识别违反架构约束的实现。例如，检查是否有上层模块直接调用了下层模块的内部接口，是否有模块绕过了定义的接口规范，前端代码是否遵循了组件规范等。

**模式标准化代理**应当验证代码是否符合项目的编码标准。对于 AI-SecOps 项目，这包括检查 Pydantic 模型的使用是否规范、异步编程模式是否一致、React 组件开发是否规范、TypeScript 类型定义是否完整等。

---

## 第三部分：上下文工程实践指南

### 3.1 项目配置文件结构

AI-SecOps 项目应当建立清晰的项目配置文件结构，确保 OpenClaw 能够快速理解项目的整体布局和关键信息。以下是推荐的文件结构：

```
ai-secops-project/
├── AI_SECOPS.md                 # 项目主配置文件（核心）
├── CLAUDE.md                    # OpenClaw 特定配置
├── features.json                 # 功能清单
├── progress.md                   # 开发进度记录
├── pyproject.toml                # Python 项目配置
├── package.json                  # 前端项目配置
├── tsconfig.json                 # TypeScript 配置
├── vite.config.ts               # Vite 构建配置
├── Dockerfile                    # 容器化配置
├── docker-compose.yml            # 多服务编排
├── Makefile                      # 构建任务定义
├── .env.example                  # 环境变量模板
├── backend/                      # 后端代码目录
│   ├── src/                     # 后端源代码
│   │   ├── layer1_flood_gate/   # 防洪网关层
│   │   ├── layer2_normalizer/   # 数据清洗层
│   │   ├── layer3_graph/        # 数据关联层
│   │   ├── layer4_compression/  # 信息压缩层
│   │   ├── layer5_analyzer/     # 威胁分析层
│   │   ├── layer6_orchestrator/ # 控制编排层
│   │   ├── layer7_simulator/    # 对抗推演层
│   │   ├── layer8_executor/     # 终端执行层
│   │   └── layer9_reporter/     # 复盘研报层
│   └── tests/                   # 后端测试
├── frontend/                     # 前端代码目录
│   ├── src/
│   │   ├── components/         # React 组件
│   │   ├── pages/              # 页面组件
│   │   ├── hooks/              # 自定义 Hooks
│   │   ├── services/           # API 服务
│   │   ├── types/               # TypeScript 类型
│   │   ├── stores/              # 状态管理
│   │   └── utils/              # 工具函数
│   ├── public/                  # 静态资源
│   └── tests/                   # 前端测试
├── configs/                     # 配置文件目录
│   ├── ocsf_schema/            # OCSF 模式定义
│   ├── stix_objects/           # STIX 对象定义
│   └── rules/                  # 过滤规则
├── scripts/                     # 脚本目录
│   └── init.sh                 # 环境初始化脚本
└── docs/                        # 文档目录
```

### 3.2 AI_SECOPS.md 核心内容

`AI_SECOPS.md` 是 AI-SecOps 项目的核心配置文件，应当包含以下内容模块：

**项目概述**部分应当简要描述 AI-SecOps 系统的目标和架构，包括系统要解决的核心问题、采用的三层能力架构和九层技术架构设计以及主要的技术选型。

**架构规范**部分应当详细定义每一层的职责、模块划分和接口定义。以下是一个示例结构：

```markdown
## 架构规范

### 第1层：防洪网关层 (layer1_flood_gate)
- **职责**：接收厂商 Webhook 推送的原始日志，进行初步规则过滤
- **核心模块**：
  - `receiver.py`：HTTP 端点接收日志
  - `filter.py`：基于 Sigma 规则的过滤引擎
  - `router.py`：消息队列路由
- **输入**：厂商原生 JSON 格式日志
- **输出**：带 trace_id 的信封格式，推送到 Redis

### 第2层：数据清洗层 (layer2_normalizer)
- **职责**：使用 DSPy 提取关键实体，输出 OCSF 标准化格式
- **核心模块**：
  - `extractor.py`：DSPy 驱动的实体提取
  - `mapper.py`：OCSF 字段映射
  - `validator.py`：Pydantic 模型校验
- **输入**：防洪网关层输出的信封
- **输出**：OCSF NormalizedIncident 对象
```

**前端架构**部分应当描述 React 应用的整体设计，包括组件层次结构、状态管理方案、路由设计以及与后端的交互方式。前端架构部分还应当包含 TypeScript 编码规范和 React 组件开发规范。

**数据标准**部分应当列出项目使用的所有数据标准，包括 OCSF 类别定义、STIX 对象类型映射、MITRE ATT&CK 战术编码、前后端 API 交互格式等。

**编码约定**部分应当规定项目使用的编程规范，包括 Python 异步编程风格（必须使用 async/await）、错误处理模式（必须使用自定义异常类）、日志规范（必须包含 trace_id）、TypeScript 类型注解要求、React 组件开发规范等。

**API 接口规范**部分应当定义前后端之间以及各层之间交互的 API 接口，包括 RESTful 端点定义、WebSocket 消息格式、请求/响应格式、错误码定义、超时设置等。

**部署指南**部分应当记录环境配置、依赖安装、服务启动、构建流程等部署相关的信息。

### 3.3 features.json 功能清单设计

`features.json` 是管理功能开发进度的核心文件，应当采用结构化的 JSON 格式，覆盖后端和前端的所有功能点。每个功能条目包含以下字段：

```json
{
  "features": [
    {
      "id": "L2-NORM-001",
      "layer": "layer2_normalizer",
      "category": "data_extraction",
      "name": "从深信服防火墙日志提取攻击者IP",
      "description": "使用 DSPy 从深信服防火墙的原始日志中提取攻击者IP地址，映射到 OCSF observables 字段",
      "priority": "high",
      "test_steps": [
        "启动开发服务器: cd backend/src/layer2_normalizer && uvicorn main:app",
        "发送测试请求: curl -X POST http://localhost:8000/normalize -d @backend/tests/fixtures/sangfor_fw_sample.json",
        "验证响应包含 attacker_ip 字段且值正确"
      ],
      "acceptance_criteria": [
        "能从深信服防火墙日志中提取 src_ip",
        "输出符合 OCSF Network Activity 类别",
        "Pydantic 校验通过",
        "处理时间小于 500ms"
      ],
      "passes": false,
      "implemented_at": null,
      "tested_by": null
    },
    {
      "id": "FE-CHAT-001",
      "layer": "frontend",
      "category": "interaction",
      "name": "自然语言查询接口",
      "description": "在 React 前端实现自然语言查询输入框，支持运维人员用自然语言提问并获取分析结果",
      "priority": "high",
      "test_steps": [
        "启动前端开发服务器: cd frontend && npm run dev",
        "在浏览器中打开 http://localhost:5173",
        "在查询输入框中输入 '最近有哪些高危告警'",
        "验证页面显示查询结果"
      ],
      "acceptance_criteria": [
        "查询输入框正常显示",
        "能够输入自然语言查询",
        "查询结果在页面正确展示",
        "WebSocket 连接正常"
      ],
      "passes": false,
      "implemented_at": null,
      "tested_by": null
    }
  ]
}
```

OpenClaw 在开发过程中应当遵循以下规则：只能修改 `passes` 字段将其设为 `true`，不能删除或修改测试步骤；只有经过实际测试验证后，才能标记功能为通过；每个功能应当独立实现和测试，避免功能之间的耦合。

### 3.4 会话启动的标准化流程

每次 OpenClaw 会话开始时，应当执行标准化的启动流程，确保代理能够快速了解项目的当前状态：

**第一步：检查工作目录和环境**。运行 `pwd` 确认当前目录，运行 `git status` 检查代码库状态，运行 `git log -5 --oneline` 查看最近的提交历史。

**第二步：读取进度文件**。读取 `progress.md` 了解本次会话之前的工作进展，读取 `features.json` 了解功能开发的整体状态，包括后端和前端两部分的进度。

**第三步：选择任务**。从 `features.json` 中选择最高优先级的未完成功能，作为本次会话的目标。注意区分后端任务和前端任务，确保选择正确的代码目录进行开发。

**第四步：启动开发环境**。运行 `init.sh` 脚本启动所需的开发服务，包括 Redis、Kafka、Neo4j 等后端依赖服务。对于前端开发，还需要启动前端开发服务器。

**第五步：验证环境健康**。执行基本的健康检查，确认所有服务正常运行后再开始编码。对于前端，需要验证 TypeScript 类型检查和 linting 通过。

**第六步：开始实现**。按照功能清单中定义的测试步骤进行开发，确保每一步都通过验证后再进行下一步。

---

## 第四部分：SOC 分析师界面开发实践指南

### 4.1 面向安全运营的前端架构设计

AI-SecOps 前端是 SOC 分析师日常工作的主战场，其设计必须紧密围绕安全运营的实际需求，以提升分析师的处置效率和决策质量为核心目标。

**组件层次结构与分析师工作流映射**。前端组件设计应当与 SOC 的 Tier 1/2/3 分析师工作流深度契合：

- **基础组件层**：提供符合安全运营习惯的通用 UI 元素，如威胁等级标识（Critical/High/Medium/Low）、MITRE ATT&CK 战术标签、设备状态指示器等。这些组件需支持暗黑模式，适应 SOC 7×24 小时值守的视觉需求。

- **业务组件层**：直接映射分析师的核心工作场景：
  - **事件队列组件**：支持按优先级、状态、资产重要性等多维度的告警筛选与排序
  - **攻击图谱可视化**：交互式展示攻击路径，支持点击查看每个节点的详细上下文
  - **智能分析卡片**：展示 AI 生成的威胁研判结论，包含置信度评分和推理依据
  - **响应操作面板**：集成一键处置按钮（隔离、阻断、取证等）和风险影响评估
  - **协作批注组件**：支持分析师在事件上添加内部备注和处置记录

- **页面组件层**：按 SOC 职能角色划分：
  - **Tier-1 值班台**：聚焦实时告警监控和初筛，界面简洁、信息密度高
  - **Tier-2 深度分析台**：提供丰富的上下文查询和关联分析工具
  - **Tier-3 专家工作台**：支持复杂的手工溯源和规则调优
  - **管理驾驶舱**：面向 SOC 主管的态势概览和团队绩效监控

**状态管理方案**需考虑 SOC 多用户协作场景。推荐使用 Zustand 配合 WebSocket 实现跨客户端状态同步，当多个分析师同时查看同一事件时，可实时感知他人的操作（如"张三正在处理此事件"的锁定提示）。全局状态应当包括：当前登录分析师信息、正在关注的事件列表、实时告警通知、系统健康状态等。

**路由设计与 SOC 权限模型对应**。基于 React Router v6 实现基于角色的访问控制：
- **分析员路由**：事件列表、事件详情、查询分析、知识库
- **响应专员路由**：处置工单、 playbook 执行、审批队列
- **主管路由**：团队看板、SLA 监控、报表中心、规则管理
- **管理员路由**：系统配置、用户管理、集成设置、审计日志

### 4.2 TypeScript 类型定义规范

前后端数据交互应当通过严格的 TypeScript 类型定义来保证类型安全。

**API 响应类型**应当与后端 Pydantic 模型保持一致。以下是一个示例：

```typescript
// frontend/src/types/api.ts

export interface EnvelopeHeader {
  trace_id: string;
  source_vendor: string;
  hit_rule_id?: string;
  priority: 'high' | 'medium' | 'low';
  received_at: string;
}

export interface OCSF_Observable {
  name: 'ip' | 'hostname' | 'file_hash' | 'user';
  value: string;
}

export interface NormalizedIncident {
  trace_id: string;
  category_uid: number;
  category_name: string;
  time: string;
  observables: OCSF_Observable[];
  attacker_ip?: string;
  victim_ip?: string;
  summary: string;
}

export interface ThreatAnalysis {
  trace_id: string;
  is_malicious: boolean;
  confidence_score: number;
  mitre_tactics: string[];
  mitre_techniques: string[];
  analysis_reasoning: string;
  recommended_actions: string[];
}

export interface HumanFeedback {
  trace_id: string;
  feedback_type: 'false_positive' | 'false_negative' | 'suggestion' | 'approval';
  content: string;
  created_at: string;
  user_id: string;
}
```

**组件 Props 类型**应当明确每个组件的输入参数。以下是一个示例：

```typescript
// frontend/src/components/ThreatEventCard/types.ts

export interface ThreatEventCardProps {
  incident: NormalizedIncident;
  analysis?: ThreatAnalysis;
  onApprove?: (traceId: string) => void;
  onReject?: (traceId: string) => void;
  onFeedback?: (feedback: HumanFeedback) => void;
}
```

### 4.3 前端与后端的通信机制

**RESTful API**用于常规的 CRUD 操作，包括获取事件列表、提交反馈、获取配置等。以下是 API 服务层的示例：

```typescript
// frontend/src/services/api.ts

import axios from 'axios';
import type { NormalizedIncident, HumanFeedback, ThreatAnalysis } from '../types/api';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
});

export const incidentApi = {
  list: (params: { page: number; page_size: number; priority?: string }) =>
    apiClient.get('/api/v1/incidents', { params }),
  
  detail: (traceId: string) =>
    apiClient.get(`/api/v1/incidents/${traceId}`),
  
  analysis: (traceId: string) =>
    apiClient.get<ThreatAnalysis>(`/api/v1/incidents/${traceId}/analysis`),
};

export const feedbackApi = {
  submit: (feedback: Omit<HumanFeedback, 'created_at' | 'user_id'>) =>
    apiClient.post('/api/v1/feedback', feedback),
  
  list: (traceId: string) =>
    apiClient.get<HumanFeedback[]>(`/api/v1/feedback`, { params: { trace_id: traceId } }),
};
```

**WebSocket**用于实时推送，包括威胁告警的实时通知、分析进度的实时更新等。以下是 WebSocket 服务的示例：

```typescript
// frontend/src/services/websocket.ts

import { useEffect, useCallback, useRef } from 'react';
import { useAppStore } from '../stores/appStore';

export type WebSocketMessage = 
  | { type: 'threat_alert'; payload: NormalizedIncident }
  | { type: 'analysis_progress'; payload: { trace_id: string; status: string } }
  | { type: 'response_result'; payload: { trace_id: string; success: boolean } };

export function useWebSocket(url: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const addNotification = useAppStore(state => state.addNotification);

  const connect = useCallback(() => {
    wsRef.current = new WebSocket(url);

    wsRef.current.onmessage = (event) => {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      switch (message.type) {
        case 'threat_alert':
          addNotification({
            type: 'warning',
            title: '新威胁告警',
            message: message.payload.summary,
          });
          break;
        // 处理其他消息类型
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current.onclose = () => {
      // 自动重连逻辑
      setTimeout(connect, 3000);
    };
  }, [url, addNotification]);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  return wsRef.current;
}
```

### 4.4 前端约束机制

**组件开发约束**是确保前端代码质量的重要手段。这些约束应当记录在 `AI_SECOPS.md` 文件中，供 OpenClaw 在开发过程中遵循：

组件命名约束方面，组件文件应当使用 PascalCase 命名，如 `ThreatEventCard.tsx`；组件目录应当使用 kebab-case 命名，如 `threat-event-card`；组件 props 接口应当使用组件名加 Props 后缀命名。

类型定义约束方面，所有 API 响应类型都应当在 `types/` 目录下集中定义；类型文件应当以 `.types.ts` 为后缀；避免使用 `any` 类型，应当使用 `unknown` 配合类型守卫。

状态管理约束方面，全局状态应当使用 Zustand 或 Redux Toolkit 管理；局部状态使用 React 的 useState；异步操作应当使用 React Query 或 SWR。

样式约束方面，优先使用 Tailwind CSS 或 CSS Modules；避免内联样式（除动态计算的值外）；保持样式与组件文件的分离。

### 4.5 前端测试策略

**单元测试**使用 Vitest 和 React Testing Library。以下是一个示例：

```typescript
// frontend/src/components/ThreatEventCard/ThreatEventCard.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { ThreatEventCard } from './ThreatEventCard';
import type { NormalizedIncident } from '../../types/api';

const mockIncident: NormalizedIncident = {
  trace_id: 'test-001',
  category_uid: 1,
  category_name: 'Network Activity',
  time: '2026-03-13T10:00:00Z',
  observables: [{ name: 'ip', value: '192.168.1.100' }],
  attacker_ip: '192.168.1.100',
  victim_ip: '10.0.0.1',
  summary: '检测到可疑网络连接',
};

describe('ThreatEventCard', () => {
  it('renders incident summary correctly', () => {
    render(<ThreatEventCard incident={mockIncident} />);
    expect(screen.getByText('检测到可疑网络连接')).toBeInTheDocument();
  });

  it('calls onApprove when approve button is clicked', () => {
    const mockOnApprove = jest.fn();
    render(
      <ThreatEventCard 
        incident={mockIncident} 
        onApprove={mockOnApprove} 
      />
    );
    
    fireEvent.click(screen.getByText('批准'));
    expect(mockOnApprove).toHaveBeenCalledWith('test-001');
  });
});
```

**E2E 测试**使用 Playwright。以下是一个示例：

```typescript
// frontend/tests/e2e/threat-query.spec.ts

import { test, expect } from '@playwright/test';

test.describe('威胁查询功能', () => {
  test('运维人员可以输入自然语言查询', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    // 登录
    await page.fill('[data-testid=username]', 'operator');
    await page.fill('[data-testid=password]', 'password');
    await page.click('[data-testid=login-button]');
    
    // 等待仪表板加载
    await expect(page.locator('[data-testid=dashboard]')).toBeVisible();
    
    // 输入自然语言查询
    await page.fill(
      '[data-testid=query-input]', 
      '最近有哪些高危告警'
    );
    await page.click('[data-testid=query-submit]');
    
    // 验证查询结果
    await expect(
      page.locator('[data-testid=query-results]')
    ).toBeVisible();
  });
});
```

---

## 第五部分：SOC 运营反馈与持续改进机制

### 5.1 分析师反馈的系统化收集

在传统 SOC 中，分析师的宝贵经验往往随着人员流动而流失，规则调优依赖少数资深专家的"手感"，缺乏系统化的知识沉淀机制。AI-SecOps 通过结构化收集一线分析师的操作反馈，实现"运营即训练"的持续改进闭环。

**反馈类型与 SOC 运营场景对应**：

| 反馈类型 | 触发场景 | 运营价值 | 数据用途 |
|---------|---------|---------|---------|
| **误报标记** | 分析师确认告警为正常业务行为 | 减少同类误报，降低分析师工作量 | 回流训练数据，优化检测模型阈值 |
| **漏报上报** | 分析师发现系统未检测到的真实攻击 | 补齐检测盲点，提升覆盖率 | 生成新的检测规则，补充到规则库 |
| **研判修正** | 分析师修改 AI 生成的分析结论 | 纠正模型偏见，提升研判准确性 | 微调 LLM 提示词，优化分析逻辑 |
| **处置效果评价** | 分析师评价自动化响应的实际效果 | 优化响应策略，减少业务影响 | 调整自动化响应的置信度阈值 |
| **知识补充** | 分析师补充 IOC、TTPs 等情报 | 丰富知识图谱，提升关联分析能力 | Enrich 到 Neo4j 图谱，供后续查询 |
| **操作偏好** | 分析师的界面布局、查询习惯 | 个性化体验，提升工作效率 | 训练用户画像模型，推荐个性化视图 |

**零摩擦反馈收集设计**。SOC 分析师工作节奏快、压力大，反馈收集必须做到"不增加额外负担"：

- **一键标记**：在事件详情页常驻"误报"按钮，点击即完成标记，无需填写表单
- **上下文自动捕获**：系统自动记录反馈时的完整上下文（原始日志、分析结论、处置动作、时间戳）
- **批处理支持**：支持对多个相似事件批量标记，适合处理误报风暴场景
- **游戏化激励**：展示分析师的贡献排名（如"本周标记误报 23 条，帮助团队节省 2.3 小时"），提升参与积极性

### 5.2 反馈数据的存储与处理

**反馈数据模型**应当结构化存储，便于后续分析。以下是反馈数据的存储模型示例：

```python
# backend/src/layer9_reporter/models/feedback.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
import uuid

class HumanFeedback(BaseModel):
    """运维人员反馈模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = Field(description="关联的事件追踪ID")
    feedback_type: Literal["false_positive", "false_negative", "suggestion", "approval"] = Field(
        description="反馈类型"
    )
    content: str = Field(description="反馈内容")
    confidence_rating: Optional[int] = Field(
        None, description="置信度评分 1-5", ge=1, le=5
    )
    metadata: dict = Field(default_factory=dict, description="额外元数据")
    user_id: str = Field(description="反馈用户ID")
    user_name: str = Field(description="反馈用户名称")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        indexes = [
            {"fields": ["trace_id"]},
            {"fields": ["feedback_type"]},
            {"fields": ["created_at"]},
        ]
```

**反馈处理流程**应当包括以下步骤：

收集阶段是指前端收集运维人员的反馈并提交到后端 API。后端验证反馈数据的完整性和有效性，并存储到数据库。分析阶段是指定期运行分析任务，对收集到的反馈数据进行统计分析，识别系统性能的瓶颈和改进方向。优化阶段是指将分析结果转化为具体的优化行动，如调整模型参数、更新规则库、改进界面设计等。

### 5.3 反馈驱动的系统优化

**误报分析**是反馈数据分析的重要内容。系统应当定期分析被标记为误报的告警，识别误报的模式和原因。以下是分析报告的示例：

```json
{
  "period": "2026-03-01 to 2026-03-13",
  "total_feedback": 156,
  "false_positive_count": 89,
  "false_positive_rate": 0.57,
  "top_fp_categories": [
    {"category": "Network Activity", "count": 34, "percentage": 0.38},
    {"category": "Malware", "count": 21, "percentage": 0.24}
  ],
  "common_patterns": [
    "业务系统在工作时间的大量正常连接被误判",
    "内部IP之间的文件传输被误判为数据外泄"
  ],
  "recommended_actions": [
    "调整 Network Activity 类的检测阈值",
    "添加业务白名单功能"
  ]
}
```

**漏报分析**同样重要。系统应当分析运维人员报告的漏报事件，评估系统是否应当检测到这些威胁。以下是分析报告的示例：

```json
{
  "period": "2026-03-01 to 2026-03-13",
  "false_negative_reports": 12,
  "detection_gaps": [
    {
      "technique": "T1059 - Command and Scripting Interpreter",
      "reported_count": 5,
      "root_cause": "缺少对 PowerShell 远程执行的检测规则"
    }
  ],
  "recommended_actions": [
    "添加 PowerShell 检测规则",
    "增强对脚本解释器的监控"
  ]
}
```

---

## 第六部分：架构约束实践指南

### 6.1 依赖分层策略

AI-SecOps 项目应当建立严格的依赖分层策略，确保模块之间的边界清晰、可维护性强。基于九层架构的特点，推荐采用以下依赖层次：

**第一层（底层）**包含数据类型定义和枚举，包括 Pydantic 模型类、STIX 对象类、OCSF 模式类、TypeScript 类型定义等。这一层不依赖任何其他业务代码。

**第二层**包含数据处理核心逻辑，包括 DSPy 提示模板、实体提取器、格式转换器等。这一层依赖第一层的数据类型定义。

**第三层**包含业务逻辑层，包括各层的核心处理模块。这一层依赖第二层的数据处理功能。

**第四层**包含编排和控制层，包括 LangGraph 状态机、Agent 协调器等。这一层依赖第三层的业务逻辑。

**第五层**包含执行和终端层，包括 OpenC2 解析器、设备 API 适配器等。这一层依赖第四层的编排指令。

**第六层**包含用户界面层，包括 React 前端应用、Web API 等。这一层可以调用所有下层模块，通过 RESTful API 和 WebSocket 进行通信。

在代码实现中，应当通过 linter 规则强制执行依赖分层。例如，可以在项目根目录配置 `pylint` 或 `ruff` 规则，禁止跨层依赖的情况发生。

### 6.2 接口契约的定义

各层之间以及前后端之间的交互应当通过清晰的接口契约进行，接口契约通过 Pydantic 模型和 TypeScript 类型定义进行定义和验证。

**后端各层之间的接口契约**已经在之前的文档中详细说明，此处不再赘述。

**前后端 API 接口契约**是前端开发的重要参考。以下是一个完整的 API 接口设计示例：

```python
# backend/src/api/routes/incidents.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["incidents"])

class IncidentListResponse(BaseModel):
    """事件列表响应"""
    total: int
    page: int
    page_size: int
    items: List[NormalizedIncident]

class IncidentDetailResponse(BaseModel):
    """事件详情响应"""
    incident: NormalizedIncident
    analysis: Optional[ThreatAnalysis] = None
    graph_context: Optional[List[str]] = None

class FeedbackRequest(BaseModel):
    """反馈提交请求"""
    trace_id: str
    feedback_type: str
    content: str
    confidence_rating: Optional[int] = Field(None, ge=1, le=5)

class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: str
    created_at: datetime
    status: str

@router.get("/incidents", response_model=IncidentListResponse)
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    priority: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """获取事件列表"""
    # 实现逻辑
    pass

@router.get("/incidents/{trace_id}", response_model=IncidentDetailResponse)
async def get_incident_detail(trace_id: str):
    """获取事件详情"""
    # 实现逻辑
    pass

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """提交运维反馈"""
    # 实现逻辑
    pass
```

### 6.3 Linter 规则配置

项目应当配置自定义的 linter 规则来强制执行架构约束。以下是推荐添加到 `pyproject.toml` 或 `ruff.toml` 的配置：

```toml
[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]
ignore = ["E501", "B008"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]

[tool.ruff.lint.custom-rules]
# 自定义规则：禁止从上层模块导入下层模块
no-upward-imports = { message = "禁止从上层模块导入下层模块" }
```

前端项目应当配置 ESLint 和 Prettier：

```json
// frontend/.eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "react/prop-types": "off"
  }
}
```

此外，可以编写自定义的 Python 脚本作为 pre-commit hook，检查以下约束：

- 检查是否有模块绕过了定义的 API 接口
- 检查 Pydantic 模型是否正确使用了必填字段验证
- 检查异步函数是否正确使用了 await
- 检查日志语句是否包含了 trace_id
- 检查前端组件是否正确使用了 TypeScript 类型

---

## 第七部分：测试与验证实践指南

### 7.1 测试层次设计

AI-SecOps 项目应当建立多层次的测试体系，确保每个组件和整体流程都经过充分验证。

**单元测试**针对最小的可测试单元进行验证，通常是单个函数或方法。单元测试应当覆盖核心的数据处理逻辑，包括 OCSF 字段映射、STIX 对象转换、过滤规则匹配、React 组件渲染等。单元测试应当具有快速执行、确定性结果的特点，每个测试应当在毫秒级完成。

**集成测试**针对多个组件之间的交互进行验证，测试数据在各层之间流转时的正确性。集成测试应当覆盖完整的处理链路，例如从 L1 接收原始日志到 L2 输出标准化格式的完整流程。集成测试可以使用内存数据库或 Docker 容器来模拟依赖服务。前端集成测试应当验证组件之间的交互、API 服务的调用、状态管理的更新等。

**端到端测试**模拟真实的安全事件场景，验证整个九层架构以及前后端的协同工作能力。端到端测试应当覆盖典型的攻击场景，例如外部 IP 对内网主机的扫描行为如何被检测、分析、决策、响应以及展示给运维人员。端到端测试可以使用 Mock 的外部服务来模拟安全设备的告警推送。

### 7.2 DSPy 验证框架

AI-SecOps 项目大量使用 DSPy 框架来构建智能分析能力，因此需要专门的验证框架来确保 DSPy 模块的质量。

**提示词验证**确保 DSPy 的提示模板能够正确引导模型输出期望的格式。验证内容包括：模型是否按照要求输出 JSON 格式、是否包含了所有必要的字段、字段类型是否正确等。

**输出校验**使用 Pydantic 模型对 DSPy 的输出进行强制校验。对于任何校验失败的情况，系统应当记录详细的错误信息，并触发自动重试或人工干预流程。

**置信度评估**对于包含置信度输出的 DSPy 模块，应当验证置信度评分与实际结果的一致性。例如，如果模型输出的置信度为 95%，则该判断在后续的验证中应该有较高的准确率。

### 7.3 自动化验证流程

每次 OpenClaw 完成代码修改后，应当触发自动化的验证流程，确保修改没有引入新的问题。推荐的自动化验证流程如下：

**第一阶段：代码质量检查**。运行 ruff 或 pylint 检查代码风格和潜在的错误，运行 mypy 进行类型检查，运行 ESLint 检查前端代码风格，运行 tsc 进行 TypeScript 类型检查。

**第二阶段：单元测试**。运行项目的所有单元测试，确保核心逻辑的正确性。单元测试的覆盖率应当保持在 80% 以上。

**第三阶段：集成测试**。运行集成测试，验证各层之间的交互是否正常。集成测试可能需要启动 Docker 容器来提供测试环境。

**第四阶段：功能验证**。根据 `features.json` 定义的测试步骤，对本次修改相关的功能进行验证。只有通过验证后才能提交代码。

### 7.4 持续集成配置

项目应当配置持续集成（CI）管道，在每次代码提交和合并请求时自动运行验证。以下是推荐的 CI 配置示例（使用 GitHub Actions）：

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-test:
    runs-on: ubuntu-22.04
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
      neo4j:
        image: neo4j:5
        ports:
          - 7474:7474
          - 7687:7687
        env:
          NEO4J_AUTH: neo4j/password
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12.8'
          
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install ruff mypy pytest pytest-cov
          
      - name: Lint
        run: |
          ruff check backend/src/ tests/
          mypy backend/src/
          
      - name: Test
        run: |
          pytest backend/tests/ -v --cov=backend/src --cov-report=xml

  frontend-test:
    runs-on: ubuntu-22.04
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          
      - name: Lint and Type check
        run: |
          cd frontend
          npm run lint
          npm run typecheck
          
      - name: Test
        run: |
          cd frontend
          npm run test:coverage
```

---

## 第八部分：长期运行 Agent 管理实践

### 8.1 会话状态管理

OpenClaw 在离散会话中工作，每个会话是独立的上下文窗口。对于 AI-SecOps 这样需要长期开发的项目，会话之间的状态管理至关重要。

**Git 提交策略**。每次会话结束前，应当将所有已完成的代码更改提交到 Git。提交消息应当清晰描述本次修改的内容，便于后续追溯。提交粒度应当适中，避免将大量不相关的修改混合在一个提交中。前端和后端代码应当分开提交，便于追踪各部分的变更历史。

**进度文件更新**。每次会话结束后，应当更新 `progress.md` 文件，记录本次会话完成的工作、遇到的问题以及下一步的计划。进度文件应当分别记录后端和前端的开发进度，确保下一次会话能够准确了解项目状态。

**环境状态记录**。如果开发环境需要特殊的配置或数据，应当将这些信息记录在专用的文件中，供后续会话参考使用。这包括前端依赖版本、后端模型配置、数据库状态等信息。

### 8.2 增量开发模式

OpenClaw 应当采用增量开发模式，每次会话只关注一个或少数几个功能点的实现。这种模式有以下优势：

**降低复杂性**。将大型系统分解为可管理的小功能点，每次只处理一个，降低了认知负担。功能和任务应当按照前后端划分，确保每个功能点的实现都在正确的代码目录中进行。

**便于验证**。每个功能点都有明确的验收标准，可以快速验证是否完成。验收标准应当包括后端 API 功能和前端展示效果两个方面。

**易于回滚**。如果某个功能实现出现问题，可以方便地回滚到之前的状态，不会影响其他功能。

**进度透明**。通过 `features.json` 可以清晰地了解项目的整体进度，包括后端和前端两部分的完成情况，便于项目管理和协调。

### 8.3 失败模式与应对策略

在长期运行的项目中，OpenClaw 可能遇到各种失败模式，需要提前设计应对策略。

**代理过早宣布完成**的应对策略是使用结构化的功能清单。每个功能都有明确的验收标准，代理必须通过实际测试才能标记为完成，不能仅凭主观判断。前端功能还需要验证浏览器中的实际渲染效果。

**代理留下不可恢复状态**的应对策略是严格的 Git 工作流。要求代理在每次修改后都提交代码，并定期推送远程仓库。如果出现问题，可以通过 Git 回滚到之前的状态。

**代理标记功能为通过但实际未通过**的应对策略是强制验证。功能清单中的测试步骤必须实际执行，代理不能跳过验证步骤。对于前端功能，必须在浏览器中实际验证渲染效果。可以在 CI 管道中添加验证关卡，确保只有真正通过测试的功能才能合并到主分支。

**代理花费大量时间探索无效路径**的应对策略是明确的约束和提示。在 `AI_SECOPS.md` 中提供具体的实现指导，包括推荐的技术方案、代码示例和注意事项，减少代理的探索成本。对于前端开发，应当提供详细的组件开发规范和 TypeScript 类型定义示例。

---

## 第九部分：安全考虑与合规要求

### 9.1 开发环境安全

AI-SecOps 项目的开发环境涉及大量的敏感数据和安全工具，需要特别注意安全防护。

**凭据管理**。所有 API 密钥、数据库密码和其他敏感凭据应当存储在环境变量或专门的密钥管理服务中，不应硬编码在代码中。项目应当提供 `.env.example` 文件作为环境变量模板，但不包含真实的凭据值。前端项目的环境变量应当使用 `VITE_` 前缀，以便 Vite 正确处理。

**依赖安全**。定期使用安全扫描工具（如 `pip-audit`、`safety`、`npm audit`）检查依赖项是否存在已知漏洞。优先使用官方维护的包，避免使用来源不明的第三方库。前端项目的 npm 依赖应当锁定版本，使用 `package-lock.json` 或 `yarn.lock`。

**代码审查**。所有代码修改都应当经过人工审查才能合并到主分支。审查重点包括安全性、合规性和架构一致性。前端代码的安全审查应当特别关注 XSS 防护、CSRF 保护等 Web 安全问题。

### 9.2 运行时安全

AI-SecOps 系统的运行时安全是核心要求，需要通过多层次的防护机制来确保。

**人类在环（HITL）机制**。对于高风险的自动化操作（如网络封禁、主机隔离），系统应当设计人类审批流程。LangGraph 的 `interrupt_before` 特性可用于实现这一机制，确保操作在执行前需要人工确认。前端应当提供清晰的审批界面，展示操作的风险和影响。

**OpenC2 执行约束**。终端执行层只接受标准化的 OpenC2 格式指令，不接受任何自由格式的命令。这种约束可以有效防止 Prompt 注入攻击导致的破坏性操作。

**沙盒执行**。所有自动化执行的指令都应当在隔离的沙盒环境中运行。沙盒应当限制网络访问权限、文件系统访问权限和系统命令执行权限，确保即使指令被恶意利用也不会造成严重后果。

**审计日志**。所有自动化操作都应当记录详细的审计日志，包括操作内容、操作时间、操作结果和审批人等信息。审计日志应当保存足够长的时间，满足合规要求。前端应当记录运维人员的关键操作，如反馈提交、审批决策等。

### 9.3 数据合规

AI-SecOps 项目处理的数据可能包含敏感的个人信息和商业机密，需要遵守相关的数据保护法规。

**数据脱敏**。在日志、报告和其他输出中，应当对敏感信息进行脱敏处理。脱敏规则应当符合行业标准和法规要求。前端展示的数据应当经过脱敏处理，隐藏敏感的个人信息。

**数据保留策略**。不同类型的数据应当有明确的保留期限，过期数据应当按照既定策略进行销毁。反馈数据的保留期限应当符合相关法规要求。

**访问控制**。系统应当实现基于角色的访问控制（RBAC），确保不同角色的用户只能访问其职责范围内所需的数据。前端应当根据用户角色显示或隐藏相应的功能模块。

---

### 1.4 MVP分层实施路线图

鉴于九层架构的复杂性，建议采用三阶段实施策略：

**Phase 1: 核心数据流（1-2个月）**
- L1 防洪网关：基础Sigma规则过滤
- L2 数据清洗：DSPy基础提取 + OCSF标准化
- L3 知识图谱：Neo4j基础节点存储
- 前端：基础拓扑画布 + 资产展示

**Phase 2: 智能分析（2-3个月）**
- L4 信息压缩：基础聚合逻辑
- L5 威胁分析：DSPy研判Agent
- L6 控制编排：LangGraph基础状态机
- 前端：AI Copilot + 告警故事线

**Phase 3: 高级能力（2-3个月）**
- L7 对抗推演：AutoGen红蓝对抗
- L8 终端执行：OpenC2协议实现
- L9 复盘研报：CrewAI报告生成
- 前端：完整HITL审批 + 反馈收集

---

## 第十部分：实施建议与最佳实践总结

### 10.1 项目启动建议
======= REPLACE


在启动一个新的 AI-SecOps 项目时，建议遵循以下步骤：

**第一步：定义项目范围**。明确系统要解决的问题、覆盖的安全场景和目标用户。项目范围的定义应当与业务方和安全团队充分沟通，确保需求清晰。明确前台交互和后台分析的职责边界。

**第二步：设计架构方案**。基于三层能力架构和九层技术架构体系，设计详细的架构方案，包括每一层的职责划分、技术选型和接口定义。架构设计应当经过技术评审，确保可行性和可维护性。前端架构设计应当与后端架构同步进行，确保 API 接口的一致性。

**第三步：建立开发环境**。创建项目结构，配置开发工具链，建立 CI/CD 管道。确保团队成员能够快速搭建本地开发环境。前端和后端的开发环境应当能够独立启动和运行。开发环境应当基于 Ubuntu 22.04 和 Python 3.12.8。

**第四步：创建基础文件**。编写 `AI_SECOPS.md`、`features.json` 等基础配置文件。功能清单应当覆盖项目的所有功能，包括后端分析和前端交互两个方面，并按照优先级排序。

**第五步：验证开发流程**。在开始大规模开发前，先用一两个简单的功能验证整个开发流程是否顺畅，包括 OpenClaw 的使用、测试的执行、CI 管道的运行以及前后端的联调。

### 10.2 团队协作建议

AI-SecOps 项目的开发通常需要多人协作，以下是团队协作的最佳实践：

**统一开发规范**。团队应当统一代码风格、命名约定和文档格式。建议在 `AI_SECOPS.md` 中详细定义这些规范，包括后端和前端两部分的规范，并使用自动化工具进行强制检查。

**定期同步会议**。定期召开项目同步会议，回顾进度、讨论问题和规划下一步工作。建议每周至少一次，每次会议时间控制在 30 分钟以内。会议应当分别讨论后端和前端的进度和挑战。

**知识共享**。将开发过程中积累的经验和教训记录下来，供团队成员参考。可以创建内部的知识库或在 `docs/` 目录下维护项目文档。知识库应当包括后端开发指南和前端开发指南两个部分。

**代码所有权**。每层架构和前端模块应当有明确的所有者，负责该层代码的质量和演进。代码审查时应当优先由所有者进行评审。

### 10.3 持续优化建议

AI-SecOps 项目是长期维护的系统，需要持续优化和改进。

**定期技术债务清理**。安排专门的时间清理技术债务，包括代码重构、文档更新和测试补充。技术债务的累积会导致开发效率下降，应当予以重视。前端代码的技术债务清理应当包括组件优化、性能提升和用户体验改进。

**性能监控与优化**。建立性能监控机制，跟踪系统的关键指标，如处理延迟、吞吐量和资源利用率。发现性能瓶颈时，应当及时进行优化。前端性能监控应当包括页面加载时间、交互响应时间和内存使用等指标。

**反馈收集与分析**。系统上线后，积极收集运维人员的反馈，分析系统的不足之处。将有价值的反馈转化为功能改进或优化建议。反馈数据的分析应当定期进行，形成优化报告。

**关注技术前沿**。AI 和安全领域的技术发展迅速，应当关注最新的研究成果和行业实践，适时引入新技术来提升系统能力。前端技术生态的更新也应当关注，适时升级依赖版本和引入新的开发工具。

---

## 附录

### 附录 A：常用命令参考

以下是 AI-SecOps 项目开发过程中常用的命令参考：

```bash
# 环境初始化
make init          # 运行 init.sh 初始化开发环境
make up            # 启动所有 Docker 服务
make down          # 停止所有 Docker 服务

# 后端开发
cd backend
make lint          # 运行后端代码风格检查
make typecheck     # 运行后端类型检查
make test          # 运行后端测试

# 前端开发
cd frontend
npm install       # 安装前端依赖
npm run dev       # 启动前端开发服务器
npm run build     # 构建前端生产版本
npm run lint      # 运行前端代码检查
npm run typecheck # 运行 TypeScript 类型检查
npm run test      # 运行前端测试

# 代码质量检查
make lint          # 运行代码风格检查（后端）
make typecheck     # 运行类型检查（后端）
make security      # 运行安全扫描

# 测试执行
make test          # 运行所有测试
make test-unit     # 运行单元测试
make test-integration  # 运行集成测试
make test-e2e      # 运行端到端测试

# 构建与部署
make build         # 构建 Docker 镜像
make deploy        # 部署到目标环境

# 开发辅助
make logs          # 查看服务日志
make shell         # 进入容器 Shell
make db-console    # 打开数据库控制台
```

### 附录 B：配置文件清单

以下是 AI-SecOps 项目应当创建的核心配置文件清单：

| 文件路径                  | 用途               | 创建时机   |
| ------------------------- | ------------------ | ---------- |
| `AI_SECOPS.md`            | 项目主配置文件     | 项目初始化 |
| `CLAUDE.md`               | OpenClaw 配置      | 项目初始化 |
| `features.json`           | 功能清单           | 项目初始化 |
| `progress.md`             | 开发进度记录       | 项目初始化 |
| `pyproject.toml`          | Python 项目配置    | 项目初始化 |
| `package.json`            | 前端项目配置       | 项目初始化 |
| `tsconfig.json`           | TypeScript 配置    | 项目初始化 |
| `vite.config.ts`          | Vite 构建配置      | 项目初始化 |
| `Dockerfile`              | 容器化配置         | 项目初始化 |
| `docker-compose.yml`      | 服务编排           | 项目初始化 |
| `Makefile`                | 构建任务           | 项目初始化 |
| `.env.example`            | 环境变量模板       | 项目初始化 |
| `.ruff.toml`              | 后端代码检查配置   | 项目初始化 |
| `.eslintrc.json`          | 前端代码检查配置   | 项目初始化 |
| `.prettierrc.json`        | 前端代码格式化配置 | 项目初始化 |
| `.pre-commit-config.yaml` | Pre-commit 配置    | 项目初始化 |

### 附录 C：术语表

以下是本文档中使用的关键术语解释：

| 术语                | 英文                     | 定义                                                         |
| ------------------- | ------------------------ | ------------------------------------------------------------ |
| Harness Engineering | Harness Engineering      | 新兴的工程学科，通过设计约束、反馈循环和环境管理使 AI 代理可靠工作 |
| 上下文工程          | Context Engineering      | 确保 AI 代理在正确时间拥有正确信息的工程实践                 |
| 熵管理              | Entropy Management       | 解决 AI 生成代码库随时间积累 drift 问题的实践                |
| 人类在环            | HITL (Human-in-the-Loop) | 在自动化流程中引入人工审批的机制                             |
| OpenC2              | OpenC2                   | OASIS 开发的标准化命令控制协议                               |
| OCSF                | OCSF                     | 开放网络安全架构框架                                         |
| STIX                | STIX                     | 结构化威胁信息表达标准                                       |
| MITRE ATT&CK        | MITRE ATT&CK             | 网络攻击战术、技术和知识库                                   |
| 误报                | False Positive           | 系统错误地将正常行为标记为威胁                               |
| 漏报                | False Negative           | 系统未能检测到真实的威胁                                     |

---

## 第十一部分：AI生成代码的审查与质量控制

### 11.1 审查流程设计

AI生成代码的质量控制是Harness Engineering的核心环节。对于AI-SecOps项目，建议采用三层审查机制：

**第一层：自动化检查（Auto-Check）**
- 所有AI生成代码必须通过 ruff + mypy + ESLint
- 单元测试覆盖率不得低于80%
- 禁止出现 `any` 类型（TypeScript）和裸 `except`（Python）
- 检查trace_id是否正确传递

**第二层：架构合规检查（Architecture Compliance）**
- 检查是否违反分层依赖规则
- 检查是否正确使用Pydantic模型
- 检查是否正确包含trace_id
- 检查是否有安全漏洞（SQL注入、命令注入风险）

**第三层：人工审查（Human Review）**
- 安全相关代码必须由安全工程师审查
- 核心算法变更需要技术负责人审查
- 前端组件需要UI一致性审查

### 11.2 禁止模式清单

| 禁止模式 | 风险 | 替代方案 |
|---------|------|---------|
| AI直接生成并执行Shell命令 | 命令注入 | 使用OpenC2标准格式 |
| 前端直接操作DOM绕过React | 状态不一致 | 使用React状态管理 |
| LLM输出直接作为SQL执行 | SQL注入 | 使用参数化查询 |
| 缺失类型注解的函数 | 类型不安全 | 强制TypeScript/Python类型 |
| 绕过HITL直接执行高危操作 | 安全风险 | 必须经过人工审批 |

### 11.3 代码质量基准

- 后端代码：mypy strict模式通过，ruff检查0警告
- 前端代码：TypeScript strict模式，ESLint 0警告
- 测试覆盖：核心逻辑80%以上覆盖率
- 性能要求：API响应时间<200ms，前端交互<100ms

---

**文档信息**

- **版本**：1.3
- **创建时间**：2026年3月14日
- **适用范围**：使用 Claude Code / Cline 开发的企业级 AI-SecOps 项目
======= REPLACE

