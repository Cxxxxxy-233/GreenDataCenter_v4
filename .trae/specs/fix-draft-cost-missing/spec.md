# 初稿生成与成本计算数据缺失修复 Spec

## Why

前端方案生成页中，**初稿生成**三张卡片（绿电分配/制冷方案/供电方案）和**成本计算**卡片的数据全部为空或为零。用户确认后端终端日志中没有出现 `[SSE PUSH] node=draft_plan_agent` 和 `[SSE PUSH] node=cost_calculation` 的输出，说明 server.py 根本没有推送这两个节点的 SSE 消息。

## 根因分析

### 后端节点确实向 streaming_output 追加了数据

通过代码审查确认：

1. **DraftPlanAgentNode** (`nodes.py:267-276`)：在返回值中追加了：
   ```python
   streaming_output.append({
       "node": "draft_plan_agent",
       "full_output": {"raw_output": output_text, "parsed": plan_data}
   })
   ```

2. **CostCalculationNode** (`nodes.py:176-182`)：在返回值中追加了：
   ```python
   streaming_output.append({
       "node": "cost_calculation", 
       "full_output": analysis_result  # 含 total_capex_lakh, capex_breakdown
   })
   ```

### 问题出在 server.py 的 astream 数据提取逻辑

server.py (`server.py:123-159`) 使用 `coordinator.compiled_graph.astream(initial_state)` 遍历节点事件。对每个事件尝试三层回退提取 `full_output`：

1. **第一层**：从 `workflows_store[workflow_id]["streaming_output"]` 查找 — 这是 server.py 自身维护的 SSE 消息列表，只包含之前已推送的节点消息，当前节点不可能在其中
2. **第二层**：从 `node_output["streaming_output"]` 查找 — 这是节点返回值中的累积列表
3. **第三层**：使用原始 `node_output`

**真正的问题**：LangGraph 的 `astream()` 在遍历有条件边（conditional edges）的图时，**可能不会对所有节点产生事件**。具体来说：
- 当 `check_budget_status` 条件边返回 `"continue"` 时，LangGraph 可能将连续的节点合并为一个超级步骤（super-step），只 yield 最后一个节点的事件
- 或者 `astream()` 默认模式可能跳过某些内部节点

这导致 draft_plan_agent 和 cost_calculation 的事件可能不被 `astream` 正常 yield，从而不会被推送到 SSE 队列。

## What Changes

### 后端 server.py 修改

- **修改 astream 数据提取的第二层查找逻辑**：不仅从 `node_output["streaming_output"]` 中查找当前节点，还要查找**所有尚未被推送的节点**
- **增加调试日志**：在每个 astream 事件中打印 `node_name` 和 `node_output` 的所有顶层 key
- **在 astream 循环结束后，补充推送缺失的节点**：对比节点追加的 `streaming_output` 和实际推送的列表，补发遗漏的节点消息

### 前端 Generate.vue 修改

- 确认 handleSSENode 中 draft_plan_agent 和 cost_calculation 的数据路径正确
- 成本计算卡片的 budget_constraint 显示 2000 说明可能有部分数据到达，需要验证完整路径

## Impact
- Affected code: `src/greendatacenter/server.py`, `frontend/src/views/Generate.vue`
- 不影响后端业务逻辑

## ADDED Requirements

### Requirement: 所有节点的 SSE 消息必须被推送

#### Scenario: draft_plan_agent 节点
- **WHEN** DraftPlanAgentNode 执行完成
- **THEN** server.py 必须推送包含 `{raw_output, parsed: {green_power_result, cooling_result, power_supply_plan}}` 的 SSE 消息

#### Scenario: cost_calculation 节点  
- **WHEN** CostCalculationNode 执行完成
- **THEN** server.py 必须推送包含 `{is_over_budget, total_capex_lakh, capex_breakdown}` 的 SSE 消息

#### Scenario: astream 未 yield 某些节点
- **WHEN** astream 循环结束但某些节点的消息未被推送
- **THEN** 从最终 state 的 streaming_output 中提取这些节点的 full_output 并补发

## MODIFIED Requirements

### Requirement: server.py astream 循环增强

当前的第二层查找只查找当前 `node_name` 的条目：
```python
for entry in reversed(inner_so):
    if entry.get("node") == node_name:
        extracted_data = entry.get("full_output")
```

修改为：同时记录哪些节点已被推送，循环结束后补发未推送的节点。
