# 前后端实时数据映射修复 Spec

## Why

前端方案生成页面存在两个严重问题：

1. **所有中间阶段卡片内容为空**：虽然节点显示"已完成"（绿色勾），但需求解析、初稿生成、成本计算、专家评审等卡片内部无任何数据展示，专家评分全部显示 0.00/5.0。这是因为 **server.py 通过 SSE 发送的是节点 `__call__` 方法的完整返回值（状态更新字典），而非有意义的数据内容**；前端 `handleSSENode` 函数按错误的路径访问数据。

2. **工作流卡在 90%（最终报告完成后、输出节点前）**：进度条到达 90%（9/10 节点）后不再推进，始终无法完成。原因是 **Output 节点的数据未被正确推送或接收**，以及可能存在的 SSE 连接超时问题。

## What Changes

### 后端 server.py 修改（不修改业务逻辑）
- **修改 SSE 数据推送结构**：当前发送的是节点的完整返回字典（如 `{user_requirement: ..., requirement: ..., current_step: ..., streaming_output: [...]}`），改为提取每个节点自行追加到 `state["streaming_output"]` 中的结构化数据（含 `full_output` 字段），该数据由各节点自身精心构建，字段清晰
- **确保 output 节点也被正确捕获和推送**

### 前端 Generate.vue 修改
- **重写 handleSSENode 的数据路径**：根据每个节点实际返回的数据结构修正字段访问路径：
  - `requirement_parser`: 数据在 `data.requirement` 中（非顶层）
  - `draft_plan_agent`: 数据在 `data.green_power_result` / `data.cooling_result` / `data.power_supply_plan`（顶层键，非 `data.parsed.xxx`）
  - `cost_calculation`: 数据在 `data.economic_analysis_result` 中（含 `total_capex_lakh`, `capex_breakdown` 等）（非顶层）
  - `economic_analysis / power_reliability_analysis / environmental_analysis`: 专家意见在 `data.economic_opinion` / `data.power_reliability_opinion` / `data.environmental_opinion` 中（经序列化后为 dict）
  - `arbitrator`: 仲裁结果在 `data.solution` 中（ArbitratorNode 返回 `{solution: solution_data}`）
  - `final_report`: 报告路径在 `data.solution.final_report_path` 中
- **增加调试日志**：在 handleSSENode 中打印收到的原始数据结构，便于排查
- **增强 SSE 断线重连逻辑**

## Impact
- Affected code: `src/greendatacenter/server.py`, `frontend/src/views/Generate.vue`
- 不影响后端任何业务逻辑（coordinator_v2.py, nodes.py, edges.py 等均不修改）

## ADDED Requirements

### Requirement: 正确的 SSE 数据推送格式

服务器端对每个 LangGraph 节点的输出，必须推送以下格式的 SSE 消息：

```json
{
  "node": "<node_name>",
  "data": {<该节点追加到 streaming_output 中的 full_output 内容>},
  "timestamp": "..."
}
```

其中 `data` 应当是各节点自行构建的 `streaming_output` 条目中的 `full_output` 字段，而非节点的完整状态更新字典。

#### Scenario: requirement_parser 节点
- **WHEN** `requirement_parser` 节点执行完成
- **THEN** 推送的 `data` 包含：`{location, planned_load_kw, green_power_ratio, ...}` （即 UserRequirement 的字段）

#### Scenario: draft_plan_agent 节点
- **WHEN** `draft_plan_agent` 节点执行完成
- **THEN** 推送的 `data` 包含：`{raw_output, parsed: {green_power_result, cooling_result, power_supply_plan}}`

#### Scenario: cost_calculation 节点
- **WHEN** `cost_calculation` 节点执行完成
- **THEN** 推送的 `data` 包含：`{is_over_budget, total_capex_lakh, budget_constraint_lakh, capex_breakdown: {power_supply_system_lakh, green_power_system_lakh}}`

#### Scenario: economic_analysis 节点
- **WHEN** `economic_analysis` 节点执行完成
- **THEN** 推送的 `data` 包含：ExpertOpinion 全部字段 `{expert_type, expert_name, summary, reasoning, scores, metrics, recommendations, concerns, confidence}`

#### Scenario: arbitrator 节点
- **WHEN** `arbitrator` 节点执行完成
- **THEN** 推送的 `data` 包含：`{name, summary, overall_scores: {economic, reliability, environmental, overall}, key_metrics, trade_offs, risks, recommendations, confidence}`

#### Scenario: final_report 节点
- **WHEN** `final_report` 节点执行完成
- **THEN** 推送的 `data` 包含：`{path: "<报告文件路径>"}` 或包含 `final_report` 和 `final_report_path`

#### Scenario: output 节点
- **WHEN** `output` 节点执行完成
- **THEN** 必须推送消息并随后发送 `completed` 信号

### Requirement: 前端正确解析并展示各阶段数据

#### Scenario: 需求解析卡片展示
- **WHEN** 收到 `requirement_parser` 节点的 SSE 数据
- **THEN** 卡片内显示：地点、总负荷(kW)、绿电目标(%)

#### Scenario: 初稿生成三卡片展示
- **WHEN** 收到 `draft_plan_agent` 节点的 SSE 数据
- **THEN** 三张卡片分别显示：光伏容量(MW)/风电容量(MW)/储能容量、制冷技术/PUE/制冷功率、Tier等级/可用性/UPS配置

#### Scenario: 成本计算卡片展示
- **WHEN** 收到 `cost_calculation` 节点的 SSE 数据
- **THEN** 卡片内显示：总投资(万元)、供电系统投资、绿电系统投资、是否超预算

#### Scenario: 专家评审三卡片展示
- **WHEN** 分别收到三位专家的 SSE 数据
- **THEN** 每张卡片显示：评分(x/5)、摘要、建议列表、关注点列表、关键指标

#### Scenario: 辩论时间线展示
- **WHEN** 收到辩论相关 SSE 数据
- **THEN** 时间线按轮次分组展示每位专家的发言内容

#### Scenario: 仲裁决策卡片展示
- **WHEN** 收到 `arbitrator` 节点的 SSE 数据
- **THEN** 卡片显示：综合评分、三方评分雷达图数据、权衡方案、置信度

#### Scenario: 工作流完成
- **WHEN** 收到 `completed` 信号
- **THEN** 进度条达到100%，显示"查看方案详情"按钮，从 completed 数据中提取最终指标

## MODIFIED Requirements

### Requirement: server.py _run_workflow 函数的 SSE 推送逻辑

当前的推送方式：
```python
# 当前（错误）：直接推送节点返回的完整状态字典
serializable_output = _make_serializable(node_output)  # node_output 是完整的 return dict
message = {"node": node_name, "data": serializable_output, ...}
```

修改为：
```python
# 修复后：优先使用节点自行构建的 streaming_output 条目
streaming_list = workflows_store.get(workflow_id, {}).get("streaming_output", [])
if streaming_list:
    last_entry = streaming_list[-1]
    if last_entry.get("node") == node_name:
        message = {"node": node_name, "data": _make_serializable(last_entry.get("full_output", node_output)), ...}
    else:
        message = {"node": node_name, "data": _make_serializable(node_output), ...}
else:
    message = {"node": node_name, "data": _make_serializable(node_output), ...}
```

### Requirement: Generate.vue handleSSENode 函数的数据映射

修正每个节点的数据访问路径，使其与后端实际推送的数据结构一致。
