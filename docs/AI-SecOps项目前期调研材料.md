# 网络安全数据规范的官方文档与最佳实践资源

## 一、OCSF (Open Cybersecurity Schema Framework)

### 📋 官方文档链接

| 资源类型       | 链接                           | 说明                   |
| -------------- | ------------------------------ | ---------------------- |
| **模式浏览器** | https://schema.ocsf.io         | 官方推荐的模式探索方式 |
| **GitHub仓库** | https://github.com/ocsf-schema | 官方源代码仓库         |
| **项目主页**   | https://ocsf.io                | 项目官方网站           |

### 📖 最佳实践

1. **统一数据格式**：OCSF提供统一的网络安全事件数据结构，解决多厂商数据格式不一致问题
2. **与存储格式无关**：OCSF与存储格式、数据采集和ETL过程无关，核心模式旨在与实现无关
3. **框架组成**：包括分类、事件类、数据类型以及属性字典
4. **主要采用厂商**：AWS、Splunk、CrowdStrike、Palo Alto Networks、Rapid7、JupiterOne等

### 🔧 快速开始

```bash
git clone https://github.com/ocsf-schema
```

------

## 二、STIX 2.1 (Structured Threat Information Expression)

### 📋 官方文档链接

| 资源类型          | 链接                                                         | 说明                        |
| ----------------- | ------------------------------------------------------------ | --------------------------- |
| **OASIS官方规范** | https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html | STIX 2.1 OASIS标准文档      |
| **OASIS CTI TC**  | https://www.oasis-open.org/committees/cti/                   | OASIS网络威胁情报技术委员会 |
| **STIX项目文档**  | http://stixproject.github.io/                                | STIX项目归档文档            |
| **TAXII规范**     | https://docs.oasis-open.org/cti/taxii/v2.1/os/taxii-v2.1-os.html | TAXII 2.1传输协议规范       |

### 📖 最佳实践

1. **核心对象类型**（19类SDO）：
   - **Indicator（指标）**：IP地址、域名、文件哈希等威胁特征
   - **Observable（可观测对象）**：具体威胁数据实例
   - **Attack Pattern（攻击模式）**：描述攻击者TTPs
   - **Malware（恶意软件）**：定义恶意软件家族或实例
   - **Report（报告）**：聚合多个STIX对象的综合分析报告
2. **使用场景**：
   - 协同威胁分析
   - 自动化威胁信息交换
   - 自动检测和响应
   - 网络安全态势感知
3. **与TAXII配合使用**：TAXII是支持STIX数据交换的传输协议，两者结合实现自动化、标准化的威胁情报共享

------

## 三、OpenC2 (Open Command and Control)

### 📋 官方文档链接

| 资源类型            | 链接                                          | 说明                   |
| ------------------- | --------------------------------------------- | ---------------------- |
| **官方网站**        | https://openc2.org/                           | OpenC2项目主页         |
| **OASIS OpenC2 TC** | https://www.oasis-open.org/committees/openc2/ | OASIS OpenC2技术委员会 |
| **规范文档**        | https://docs.oasis-open.org/openc2/           | OASIS OpenC2规范文档库 |

### 📖 最佳实践

1. **标准化命令语言**：OpenC2提供供应商和应用无关的机器间通信通用语言
2. **互操作性**：实现跨厂商、跨平台的安全控制命令标准化与自动化执行
3. **主要功能**：
   - 网络安全设备的指挥与控制
   - 支持多种防御技术的标准化命令
   - 实现自动化威胁响应工作流
4. **集成示例**：
   - 思科SecureX Orchestrator与OpenC2标准集成
   - 通过Webhook机制接收OpenC2命令请求
   - 在安全平台上自动解析并执行命令

# 网络安全运营五大核心环节的数据规范，在**国内外主流安全厂商和产品**中的实际应用清单

### 1. 遥测数据与日志标准 (Telemetry & Log)
**核心规范：OCSF (开放网络安全架构框架)、ECS (Elastic 通用模式)**

*   **国际主流厂商/产品：**
    *   **AWS (亚马逊云)**：其 **Amazon Security Lake** 是全球首个原生且全面采用 OCSF 标准构建的安全数据湖产品。
    *   **Splunk (已被Cisco收购)**：作为 OCSF 的核心发起者，其最新的 **Splunk Enterprise Security (ES)** 深度支持 OCSF，用于标准化接入海量日志。
    *   **Elastic**：毫无疑问，其 **Elastic Security (SIEM)** 和 ELK 栈原生使用自带的 **ECS** 标准，全球无数企业（包括国内企业）都基于 ECS 构建底层日志源。
    *   **IBM**：**QRadar SIEM** 正在向 OCSF 架构转型，以支持异构云环境的数据接入。
    *   **CrowdStrike**：其下一代日志管理平台 **Falcon LogScale** (前身为 Humio) 积极参与并支持 OCSF 标准的解析转换。
*   **国内主流厂商/产品：**
    *   国内大部分厂商早期使用私有 Schema，但由于出海需求和大数据架构的普及，正在向标准靠拢。
    *   **阿里云**：其 **日志服务 (SLS) 和 云安全中心** 的安全数据底座支持与 OCSF/ECS 结构进行映射，方便对接国际 SIEM 平台。
    *   **深信服 (Sangfor)**：其 **XDR** 平台的底层数据中台参考了 ECS 等国际标准来拉平各家终端和网络设备的数据字段。
    *   **奇安信**：**NGSOC (态势感知)** 支持通过 Logstash 等组件将各类异构 syslogs 标准化为类似 ECS 的统一宽表结构。

### 2. 威胁检测与分析规范 (Detection Engineering)
**核心规范：Sigma (日志检测)、YARA (文件检测)、Snort/Suricata (流量检测)**

*   **国际主流厂商/产品：**
    *   **SOC Prime**：全球最大的检测代码库，完全基于 **Sigma** 规则构建，一键将 Sigma 翻译为全球 30 多种 SIEM/EDR 的查询语句。
    *   **VirusTotal (Google Chronicle)**：**YARA** 规则的“大本营”，全球安全分析师都在使用 VT 的 YARA 引擎进行恶意样本狩猎。
    *   **Cisco (思科)**：拥有并维护 **Snort** 引擎，广泛用于其 Firepower IPS/IDS 中。
    *   **Corelight**：基于开源 **Zeek / Suricata** 构建的网络流量分析 (NTA) 顶尖厂商。
*   **国内主流厂商/产品：**
    *   **微步在线 (ThreatBook)**：其 **TDP (威胁感知平台)** 和 **OneDNS** 深度依赖标准化的检测规则，并支持引入和导出 YARA/Suricata 规则进行高级狩猎。
    *   **长亭科技**：在攻防演练中，其安全分析团队及产品广泛使用 **Sigma** 编写和共享跨平台的行为检测规则。
    *   **安天 (Antiy)**：作为国内老牌反病毒厂商，其检测引擎（AVL SDK）底层对 **YARA** 规则有极其完善的支持。
    *   **绿盟科技 (NSFOCUS) & 启明星辰 (Venustech)**：其传统的 **IPS/IDS** 和全流量检测设备底层大量兼容或基于改进的 **Snort/Suricata** 规则引擎。

### 3. 告警分类与战术框架 (Alert Taxonomy)
**核心规范：MITRE ATT&CK**
*(注：这是目前普及率最高的标准，可以说是安全的“九九乘法表”，国内外几乎所有厂商的现代化产品都在使用。)*

*   **国际主流厂商/产品：**
    *   **Palo Alto Networks (Cortex XDR)**、**CrowdStrike (Falcon XDR)**、**Microsoft (Defender XDR)**、**Mandiant**：这些头部的 EDR/XDR 产品，在其告警详情页中，100% 会将告警直接映射到 ATT&CK 的 Tactic (战术) 和 Technique (技术) 编号（如 T1059.001）。
*   **国内主流厂商/产品：**
    *   **奇安信 (天擎 EDR / 态势感知)**：在告警大屏和威胁分析页面，完整提供 ATT&CK 矩阵点亮图。
    *   **亚信安全**、**天融信**、**深信服**、**腾讯安全 (SOC)**、**字节跳动 (火山引擎安全)**：无论是云原生安全态势管理 (CSPM) 还是主机安全 (CWPP)，均已全面接入 ATT&CK 标签体系，用于评估企业的“战术覆盖率”。

### 4. 威胁情报共享与图谱构建 (CTI & Graph)
**核心规范：STIX 2.1 / TAXII 2.1**

*   **国际主流厂商/产品：**
    *   **Filigran (OpenCTI)**：目前全球最火的开源威胁情报平台，**底层数据模型 100% 原生基于 STIX 2.1 规范构建**，是 STIX 2.1 落地的最佳标杆。
    *   **MISP (恶意软件信息共享平台)**：欧洲刑警组织支持的开源情报平台，全面支持 STIX/TAXII 格式的双向导入导出。
    *   **ThreatConnect / Anomali / EclecticIQ**：全球三大商业 TIP（威胁情报平台）巨头，全面基于 STIX/TAXII 2.x 实现自动化情报交换。
    *   **IBM X-Force / 记录未来 (Recorded Future)**：顶级商业情报源，提供 TAXII Server 供客户订阅 STIX 格式的情报包。
*   **国内主流厂商/产品：**
    *   **微步在线 (ThreatBook)**：国内威胁情报龙头，其 TIP（威胁情报管理平台）和云端 API 全面支持通过 STIX / TAXII 标准下发和同步高价值 IOC 与 APT 组织情报。
    *   **奇安信 (ALPHA 威胁情报中心)**：其本地化情报平台支持摄取外部的 STIX/TAXII 威胁数据源。
    *   **绿盟 (NTI) / 恒安嘉新**：威胁情报网关和态势感知平台均预留了 STIX 格式接口，以满足金融、运营商客户与国家监管机构/行业 ISAC (信息共享与分析中心) 的标准情报对接要求。

### 5. 安全编排与自动化响应 (SOAR)
**核心规范：CACAO (剧本规范) / OpenC2 (指令控制)**
*(注：相比 STIX，CACAO 是相对较新的标准，目前各厂商的 SOAR 虽然核心逻辑一致，但在剧本格式的绝对标准化上还在演进中。)*

*   **国际主流厂商/产品：**
    *   **Palo Alto Networks (Cortex XSOAR / 前 Demisto)**：全球 SOAR 市场领导者。其剧本 (Playbooks) 使用 JSON/YAML 结构，高度模块化，积极参与并兼容 OASIS 组织的编排标准理念。
    *   **Splunk SOAR (前 Phantom)**、**Fortinet (FortiSOAR)**：采用标准化的应用层协议和 RESTful API 与异构设备联动，内部工作流剧本的设计模型与 CACAO 规范高度一致。
    *   **OASIS 联盟成员**：Cisco、Symantec、McAfee 等正在其实验室和下一代安全架构中积极推进 OpenC2 和 CACAO 的原生支持。
*   **国内主流厂商/产品：**
    *   **雾帜智能 (HoneyGuide)**：国内专注 SOAR 的代表企业，其剧本编排引擎采用标准化的数据结构与数百款主流安全产品（国内外防火墙、EDR、云平台）进行 API 对接联动。
    *   **奇安信 (SOAR)**、**启明星辰 (SOAR)**、**盛邦安全**：随着国内大型攻防演练“自动化封堵”需求的爆发，这些厂商的 SOAR 产品都在推动剧本的 JSON 代码化和标准化存储，方便在集团总部与分子公司之间下发“标准应急剧本”。



---



# 企业内部网络现状：环境太碎、产品太杂、数据格式千奇百怪

对于一个已经完成网络安全建设的企业内部网络，环境现在的状况：
1.每台终端上安装了行为监测，每天产生大量的行为日志
2.网络中不断地分析来往数据包
3.型号厂家各异的安全设备，实时分析，上报告警
4.安全设备进行异构日志、告警数据关联，识别真正的威胁，生成威胁事件，并采取协同联防。
5.数据格式完全没有遵循任何的标准规范，环境太碎、产品太杂、数据格式千奇百怪。

现在想在此基础上构建智能化网络安全运维系统：
怎么把这些数据盘活，怎么结合LLM和智能算法能力，构建智能运维AI：
1.在后台实时分析威胁，给出生成策略，自动响应处理，协同联防；
2.在前台提供与真人运维人员的交互，提供动态和丰富的界面，前台与后台“LLM推理和行动”联动；
3.收集真人运维人员参与时的操作与反馈，为系统迭代和优化提供数据支持；



---



# AI-SecOps（智能安全运营）顶层架构设计

结合网络安全实战和前面讨论的 STIX 2.1 / OCSF 规范，对9 层架构进行深度拆解、技术印证以及“锦上添花”的增强建议：

### 🛡️ 1. 防洪网关层（CPU 规则过滤）—— **战术核心：保卫 GPU**
*   **架构印证**：极其明智。安全领域的流量是海量的（EPS 动辄上万），用 LLM 去看全量日志等于把钞票扔进碎纸机。
*   **落地建议**：这里可以无缝接入传统的 **Sigma、YARA 或 Suricata 规则引擎**。基于 Rust 或 Go 编写的高性能流处理引擎（如 Vector 或 Vector.dev）比单纯的 FastAPI 性能更猛。将命中基线规则的常规告警直接静默或低成本处理，只有“罕见组合”或“规则无法判定”的高熵值可疑序列，才推入 Redis/Kafka 队列。

### 🧹 2. 数据清洗与提取层（DSPy + Pydantic）—— **战术核心：斩断幻觉**
*   **架构印证**：**这是全链路最惊艳的一笔。** 传统的 Prompt Engineering 在处理千奇百怪的安全异构日志时极度脆弱。**DSPy** 的本质不是写提示词，而是“编译”提示词。结合 Pydantic 的强制校验，强迫 LLM 输出标准化的结构（类似于强行洗出 OCSF 格式或 STIX `Observed Data`）。
*   **增强建议**：在这里定义好您的 `NormalizedIncident` 契约。如果大模型输出的 JSON 缺字段或格式错误，利用 DSPy 的 `Assert` 机制和重试回退逻辑进行自纠正，彻底消灭“数据格式幻觉”。

### 🕸️ 3. 数据关联层（Neo4j 知识图谱）—— **战术核心：降维打击**
*   **架构印证**：碎片化数据一旦变为结构化实体，立刻存入 Neo4j。这就完美对应了 **STIX 2.1 的 SRO（关系对象）** 的落地。
*   **增强建议**：建立安全本体（Ontology），例如 `(IP)-[发起]->(攻击)->[命中]->(规则)`。这让后续的查询不再是查表，而是图遍历（Graph Traversal），这对于发现隐蔽的 APT 潜伏链路（如横向移动）是降维打击。

### 🗜️ 4. 信息聚合、压缩层 —— **战术核心：破解上下文窗口灾难**
*   **架构印证**：图数据库查出来的关联数据往往是爆炸的。如果不做压缩直接丢给分析层 LLM，会引发“Lost in the Middle（中间注意力丢失）”和 Token 成本失控。
*   **增强建议**：可以采用**基于时序的合并（Time-window Aggregation）**和**图嵌入算法（Graph Embedding，如 Node2Vec）**。把“同一 IP 在 5 分钟内的 200 次爆破”压缩成一条超级摘要：“[08:00-08:05] IP(X) 执行 200 次 RDP 爆破，提取特征词为 Administrator”。

### 🧠 5. 威胁分析层（DSPy 驱动的分析 Agent）—— **战术核心：数据飞轮与微调**
*   **架构印证**：再次使用 DSPy 构建分析器，绝了。DSPy 最强大的地方在于它的 **Teleprompter（自动优化器）**。
*   **闭环设计**：这一层非常契合“人类反馈强化学习”。当后续的人类运维专家在工单上点了“误报（False Positive）”或“漏报（False Negative）”，这个反馈会作为 DSPy 的 `Metric` 传回来，DSPy 会在后台自动重新编译和更新这部分分析 Prompt，使得分析 Agent 越用越准。

### 🚦 6. 控制中枢与编排层（LangGraph）—— **战术核心：工业级状态机与 HITL**
*   **架构印证**：**LangGraph 是做 SOAR（安全编排自动化与响应）的完美引擎。** 真实的安全响应不是线性的，而是充满循环、分支和等待的。
*   **落地建议**：利用 LangGraph 的 `interrupt_before` 和 `interrupt_after` 特性，在生成封堵策略后挂起状态机。前台 UI 通过 WebSocket 收到卡片，运维人员点击【同意】，状态机从 PostgreSQL 恢复上下文，继续走向执行节点。这实现了完全可控的**人类在环（HITL）**，满足了极高的合规要求。

### ⚔️ 7. 深度对抗与溯源推演层（AutoGen）—— **战术核心：红蓝脑暴**
*   **架构印证**：对付已知威胁走 Layer 6，对付未知的高级 APT 唤醒 AutoGen。AutoGen 的多 Agent 辩论（Debate）机制非常适合需要“发散思维”的溯源。
*   **增强建议**：可以设置三个角色设定：`Red_Team_Attacker`（猜测下一步攻击）、`Blue_Team_Defender`（寻找防御盲点）和 `Threat_Intel_Analyst`（匹配外部情报库）。它们在沙盒里吵架和推演，最后把结论（Kill Chain 映射到 MITRE ATT&CK）汇总交给人类，**且严格遵循“只读图谱，不给 API 执行权限”的安全底线**。

### 💥 8. 终端执行层（pi-mono Agent+沙盒守护进程）—— **战术核心：零信任执行**
*   **架构印证**：极简、限流、阅后即焚（Ephemeral Sandbox）。这是最高级别的安全设计。把大模型生成的指令（如封禁脚本）直接下发给底层是很危险的（防范 Prompt Injection 导致自杀式命令如 `rm -rf /`）。
*   **增强建议**：引入 **OpenC2 标准** 作为指令契约。利用轻量级容器（如 Firecracker MicroVMs 或 Docker）拉起环境，执行完毕立刻销毁，并在外部挂载严格的 `AppArmor/SELinux` 策略，阻断任何越权调用。

### 📝 9. 复盘与研报层（CrewAI）—— **战术核心：释放人力**
*   **架构印证**：CrewAI 天然适合“角色扮演的流水线工作”。写报告是安全人员最讨厌但又最需要体现专业度的工作。
*   **落地建议**：配置 `Forensic_Expert`（提取时间线和技术指标 IOCs）和 `PR_Manager`（转化为管理层看得懂的商业风险描述）。不仅生成内部排版精美的 Markdown/PDF，还可以直接生成符合监管上报要求的脱敏格式文件。

---



### 工程落地的唯一挑战：链路延迟与可观测性

多层 Agent 流转极易导致排障困难。建议在全链路引入如 **LangSmith** 或 **Arize Phoenix** 等大模型可观测性工具（LLMOps），给每一次 API 调用、每一次 DSPy 断言、每一次 LangGraph 状态流转都打上 `Trace_ID`。这样，前台人类运维不仅能看到最终结论，还能像看“透明厨房”一样，清晰追溯到数据是怎么一步步从“防洪网关”流转到“终端沙盒”的。

如果您能将这套蓝图在企业中落地，这将是颠覆传统 SOC（安全运营中心），跨入下一代 AI-Native SecOps 的超级标杆。



---



# AI-SecOps（智能安全运营）架构每层详细规范与接口定义

### 🛡️ 第1层：防洪网关层（规则过滤）
*   **推荐规范**：**自定义信封包装（Envelope Schema）**。此时数据太脏，强行套标准会报错，只需加一层“路由信封”。
*   **核心逻辑**：FastAPI 接收各厂商 Webhook，正则/IP库匹配。如果是白名单直接丢弃；命中的扔进 Redis 消息队列。
*   **接口示例 (Python/JSON)**：
```json
// 【Input】: 厂商原生乱码日志 (例如一台老旧的深信服防火墙)
{
  "src_ip": "192.168.1.100",
  "dst": "8.8.8.8",
  "msg": "Malicious traffic detected signature=10023",
  "time": "2026-03-12T09:41:00Z"
}

// 【Output】 (推入 Redis 的格式): 附带了初步路由标记
{
  "trace_id": "req-99a8b7", // 贯穿整个9层架构的唯一生命周期ID
  "source_vendor": "sangfor_fw",
  "hit_rule_id": "rule_regex_sql_inject", // 命中了网关层的哪条基础正则
  "priority": "high", // CPU层初步判定的优先级
  "raw_payload": "{\"src_ip\":...}" // 原始日志作为纯字符串保留，防丢失
}
```

---

### 🧹 第2层：数据清洗与提取层（DSPy）
*   **推荐规范**：**OCSF (Open Cybersecurity Schema Framework)** 标准。
*   **核心逻辑**：DSPy 控制的大模型从 `raw_payload` 中提取关键实体，强制映射为 Pydantic 定义的 OCSF `Security Finding` 对象，斩断幻觉。
*   **接口示例 (Pydantic / 强类型输出)**：
```python
# 【Output】 (给下游的规范化输出，DSPy 强制生成的 Pydantic 模型)
class OCSF_Observable(BaseModel):
    name: str = Field(description="实体类型，如 ip, hostname, file_hash")
    value: str = Field(description="实体值")

class NormalizedIncident(BaseModel):
    trace_id: str
    category_name: str = Field(description="OCSF分类，如 Network Activity, Malware")
    time: str = Field(description="ISO8601标准时间")
    observables: List[OCSF_Observable] = Field(description="提取出的实体网络观测对象")
    attacker_ip: Optional[str] = Field(description="如果能确认，提取攻击者IP")
    victim_ip: Optional[str] = Field(description="受害者IP")
    summary: str = Field(description="一句话总结(少于50字)")

# 实例 JSON：
{
  "trace_id": "req-99a8b7",
  "category_name": "Network Activity",
  "time": "2026-03-12T09:41:00Z",
  "observables":[
    {"name": "ip", "value": "192.168.1.100"},
    {"name": "ip", "value": "8.8.8.8"}
  ],
  "attacker_ip": "8.8.8.8",
  "victim_ip": "192.168.1.100",
  "summary": "内网主机与外部恶意IP产生异常网络通信"
}
```

---

### 🕸️ 第3层：数据关联层（Neo4j 图谱）
*   **推荐规范**：**STIX 2.1 (SDO / SCO / SRO)**
*   **核心逻辑**：将 L2 输出的 OCSF 转换为 STIX 2.1 节点存入 Neo4j。IP 转为 `ipv4-addr`，日志事件转为 `Observed Data`。
*   **接口示例 (Cypher / STIX JSON)**：
```json
// 【Input】: L2的 NormalizedIncident
// 【Neo4j 内部存储格式 / Output】: STIX 2.1 格式的子图 (Sub-graph)
{
  "type": "bundle",
  "objects":[
    {
      "type": "ipv4-addr",
      "id": "ipv4-addr--ff26c055-6336-5bc5-b98d-13d6226742dd",
      "value": "8.8.8.8"
    },
    {
      "type": "incident",
      "id": "incident--001",
      "name": "Suspicious DB connection",
      "created": "2026-03-12T09:41:00.000Z"
    },
    {
      "type": "relationship",
      "id": "relationship--002",
      "relationship_type": "attributed-to",
      "source_ref": "incident--001",
      "target_ref": "ipv4-addr--ff26c055-6336-5bc5-b98d-13d6226742dd"
    }
  ]
}
```

---

### 🗜️ 第4层：信息聚合、压缩层
*   **推荐规范**：**Markdown / 密集 JSON (LLM Context Format)**
*   **核心逻辑**：大模型不需要看 STIX 的长串 UUID，需要将图数据库中查询到的周围 3 度的节点，压缩成高信息密度的文本，喂给大模型。
*   **接口示例**：
```json
// 【Output】 (给 L5 分析层的压缩上下文 Context)
{
  "trace_id": "req-99a8b7",
  "graph_context": [
    "实体[IP: 8.8.8.8] 在过去 24 小时内关联了 3 个高危告警。",
    "该 IP 曾被 [威胁情报: 微步] 标记为 [Lazarus 组织] 节点。",
    "受害主机[IP: 192.168.1.100] 上运行着存在 CVE-2021-44228 漏洞的 Java 进程。"
  ]
}
```

---

### 🕵️ 第5层：威胁分析层（DSPy Agent）
*   **推荐规范**：**MITRE ATT&CK 框架映射**
*   **核心逻辑**：结合 L2 的单点日志和 L4 的图谱上下文，大模型输出最终的定性分析结果，明确战术意图和置信度。
*   **接口示例 (Pydantic / 强类型输出)**：
```json
// 【Output】 (分析研判结论)
{
  "trace_id": "req-99a8b7",
  "is_malicious": true,
  "confidence_score": 95,  // 0-100的置信度，决定是否触发阻断
  "mitre_tactics": ["TA0011 (Command and Control)"],
  "mitre_techniques": ["T1071.001 (Web Protocols)"],
  "analysis_reasoning": "结合图谱历史，该外网IP为已知黑客组织C2节点，且受害主机存在Log4j漏洞，确认为成功利用后的心跳外连行为。",
  "recommended_actions":["ISOLATE_HOST", "BLOCK_IP"]
}
```

---

### 🚦 第6层：控制中枢与编排层（LangGraph）
*   **推荐规范**：**LangGraph State / CACAO 剧本状态机**
*   **核心逻辑**：流转状态。判断 `confidence_score`。如果大于 90，生成阻断策略并触发 `Interrupt`，推送到前端由真人审批 (HITL)。
*   **接口示例 (状态机字典 State)**：
```python
# 【LangGraph 内存中流转的 State / 提供给前台界面的卡片数据】
{
  "trace_id": "req-99a8b7",
  "current_node": "human_approval_wait", # 当前停留在等待人类审批节点
  "incident_severity": "CRITICAL",
  "proposed_playbook": { # 拟执行的动作
    "step_1": {"action": "EDR_ISOLATE", "target": "192.168.1.100", "status": "pending"},
    "step_2": {"action": "FW_BLOCK", "target": "8.8.8.8", "status": "pending"}
  },
  "human_decision": null # 等待前端调用 API 填入 "APPROVE" 或 "REJECT"
}
```

---

### ⚔️ 第7层：深度对抗与溯源推演层（AutoGen）
*   **推荐规范**：**STIX 2.1 `Campaign` (攻击活动) / `Attack Pattern`**
*   **核心逻辑**：针对未知或复杂的 APT，红蓝 Agent 在后台聊天推演，不产生实际行动，只产出预测的杀伤链（Kill Chain）。
*   **接口示例**：
```json
// 【Output】 (给分析师看的预测视图)
{
  "trace_id": "req-99a8b7",
  "simulation_result": {
    "predicted_next_steps":[
      {"technique": "T1003 (OS Credential Dumping)", "probability": 0.85},
      {"technique": "T1021.001 (Remote Desktop Protocol)", "probability": 0.70}
    ],
    "red_team_agent_thought": "我已经获取了 192.168.1.100 的权限，接下来我会尝试抓取 lsass.exe 内存获取域管理员凭证...",
    "defense_suggestion": "立即开启 EDR 的 Lsass 保护模块，并监控内网 RDP 43389 端口横向移动。"
  }
}
```

---

### 🔧 第8层：终端执行层（pi-mono Agent 沙盒）
*   **推荐规范**：**OpenC2 (Open Command and Control)**
*   **核心逻辑**：人类在前台点击“同意”后，L6 下发指令给 L8。L8 的沙盒只接受最严格的 OpenC2 格式（彻底防 Prompt 注入），然后将其翻译为具体的 API（如调用 Palo Alto 的 API）。
*   **接口示例 (严格的 OpenC2 格式)**：
```json
// 【Input】 (沙盒接收的命令，非常纯粹的动宾结构，没有废话)
{
  "action": "deny",  // 动作：拒绝/封禁
  "target": {
    "ipv4_connection": {
      "src_addr": "192.168.1.100",
      "dst_addr": "8.8.8.8"
    }
  },
  "args": {
    "duration": "PT24H"  // 封禁时间：24小时 (ISO 8601 Duration)
  },
  "actuator": { // 执行器要求
    "network_firewall": {
      "vendor": "sangfor"
    }
  }
}

// 【Output】 (执行完毕回调给 L6 的确认)
{
  "status": 200,
  "status_text": "Successfully blocked on Sangfor FW-01"
}
```

---

### 📄 第9层：复盘与研报层（CrewAI）
*   **推荐规范**：**STIX 2.1 `Report` 对象 + Markdown 文本**
*   **核心逻辑**：事件闭环后，从 Postgres 数据库拉取 `trace_id` 的所有日志，CrewAI 的“主笔 Agent”生成老板爱看的研报。
*   **接口示例**：
```json
// 【Output】: 既包含人类可读的 Markdown，又包含机器可读的情报
{
  "trace_id": "req-99a8b7",
  "human_readable_report": "# 安全事件复盘报告\n## 1. 概述\n本次事件发生于... \n## 2. 攻击者手法 (MITRE TTPs)\n- TA0011...\n## 3. 处置结果\n已通过 OpenC2 协议封禁...",
  
  "stix_report_bundle": { // 标准 STIX 2.1 报告格式，用于归档或共享给监管
    "type": "report",
    "id": "report--8e0e5a99-9fb5-4424-aa61-e0c1da0ea15f",
    "name": "APT Lazarus 数据库入侵未遂事件复盘",
    "published": "2026-03-12T10:00:00Z",
    "object_refs":[
      "incident--001",
      "ipv4-addr--ff26c055-6336-5bc5-b98d-13d6226742dd"
    ]
  }
}
```
