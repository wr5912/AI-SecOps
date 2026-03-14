// AI-SecOps Neo4j 初始数据种子
// 创建示例资产节点和关系

// 1. 创建资产节点
CREATE (dc:DataCenter {id: 'dc-beijing-01', name: '北京数据中心', location: 'Beijing'})
CREATE (dmz:NetworkZone {id: 'zone-dmz', name: 'DMZ区', type: 'dmz'})
CREATE (internal:NetworkZone {id: 'zone-internal', name: '内网区', type: 'internal'})

// 2. 创建服务器资产
CREATE (web1:Asset:Server {
  id: 'srv-web-001',
  name: 'Web服务器-01',
  ip: '10.0.0.50',
  os: 'Ubuntu 22.04',
  type: 'server',
  status: 'normal',
  risk_score: 75,
  department: 'IT运维部',
  owner: '张三'
})

CREATE (db1:Asset:Database {
  id: 'srv-db-001',
  name: 'MySQL主库',
  ip: '10.0.0.30',
  os: 'CentOS 8',
  type: 'database',
  status: 'warning',
  risk_score: 95,
  department: '数据平台部',
  owner: '李四'
})

CREATE (workstation1:Asset:Endpoint {
  id: 'ws-001',
  name: '开发工作站-A',
  ip: '10.0.0.25',
  os: 'Windows 11',
  type: 'endpoint',
  status: 'critical',
  risk_score: 85,
  department: '研发部',
  owner: '王五'
})

CREATE (firewall1:Asset:Firewall {
  id: 'fw-001',
  name: '边界防火墙',
  ip: '192.168.1.1',
  vendor: 'Sangfor',
  type: 'firewall',
  status: 'normal',
  risk_score: 40,
  department: '安全部',
  owner: '赵六'
})

// 3. 创建威胁实体节点
CREATE (attacker_ip:IPAddress {
  id: 'ip-185.220.101.42',
  address: '185.220.101.42',
  reputation: 'malicious',
  threat_type: 'C2服务器',
  first_seen: datetime()
})

CREATE (malicious_domain:Domain {
  id: 'domain-malicious-c2',
  name: 'malicious-c2.com',
  reputation: 'malicious',
  threat_type: 'C2域名'
})

// 4. 创建关系
CREATE (dc)-[:CONTAINS]->(dmz)
CREATE (dc)-[:CONTAINS]->(internal)
CREATE (dmz)-[:CONTAINS]->(web1)
CREATE (internal)-[:CONTAINS]->(db1)
CREATE (internal)-[:CONTAINS]->(workstation1)

CREATE (web1)-[:CONNECTS_TO {port: 3306, protocol: 'TCP'}]->(db1)
CREATE (workstation1)-[:CONNECTS_TO {port: 445, protocol: 'SMB'}]->(db1)
CREATE (firewall1)-[:PROTECTS]->(dmz)
CREATE (firewall1)-[:PROTECTS]->(internal)

CREATE (attacker_ip)-[:ATTACKS {timestamp: datetime(), technique: 'T1190'}]->(web1)
CREATE (attacker_ip)-[:COMMUNICATES_WITH {timestamp: datetime(), technique: 'C2'}]->(workstation1)
CREATE (workstation1)-[:RESOLVES]->(malicious_domain)

// 5. 创建告警事件
CREATE (alert1:Alert {
  id: 'alert-20260314-001',
  trace_id: 'trk-99a8b7c6',
  title: 'SQL注入尝试',
  severity: 'high',
  timestamp: datetime(),
  status: 'open',
  category: 'Web Application Attack',
  mitre_tactic: 'TA0001',
  mitre_technique: 'T1190'
})

CREATE (alert2:Alert {
  id: 'alert-20260314-002',
  trace_id: 'trk-7c3d11f9',
  title: 'C2通信检测',
  severity: 'critical',
  timestamp: datetime(),
  status: 'open',
  category: 'Command and Control',
  mitre_tactic: 'TA0011',
  mitre_technique: 'T1071'
})

// 6. 告警与资产关系
CREATE (alert1)-[:TARGETS]->(web1)
CREATE (alert2)-[:INVOLVES]->(workstation1)
CREATE (alert2)-[:INVOLVES]->(attacker_ip);

// 7. 创建索引
CREATE INDEX asset_ip_index FOR (a:Asset) ON (a.ip);
CREATE INDEX asset_id_index FOR (a:Asset) ON (a.id);
CREATE INDEX alert_trace_id_index FOR (a:Alert) ON (a.trace_id);
CREATE INDEX ip_address_index FOR (i:IPAddress) ON (i.address);
CREATE INDEX domain_name_index FOR (d:Domain) ON (d.name);