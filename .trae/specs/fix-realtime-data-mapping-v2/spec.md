# 前端实时数据展示修复 Spec v2

## Why

上一轮修复后，前端方案生成页仍存在三个未解决问题：

1. **需求解析/初稿生成/成本计算卡片内容为空**：虽然节点显示绿色完成标记，但三张卡片内部无任何数据。专家评审卡片已有数据（证明SSE通道基本正常），说明早期节点的数据路径仍有偏差或存在静默错误。

2. **专家评分格式错误**：后端 ExpertOpinion 的 `confidence` 字段是 0-1 小数（如 0.85），但前端用 `getMainScore(scores) * 5` 转换为五分制（如 4.25/5.0），与后端输出不一致。用户要求直接使用后端的 confidence 值。

3. **工作流卡在 90%**：后端程序已全部执行完毕（日志显示到 Overall score: 0.87），但前端进度停在 90%（节点10"输出"为灰色），无法到达 100%，不出现"查看方案详情"按钮。根因是 `output` 节点的事件可能未被 LangGraph 的 `astream` 正常 yield，导致 completed 信号无法发送。

## What Changes

### 后端 server.py 修改（仅修改数据推送层，不改业务逻辑）

- **确保 astream 循环结束后强制推送 output 节点和 completed 信号**：LangGraph 的 `astream` 在某些情况下可能不 yield 最后一个节点（尤其是连接到 END 的节点）的事件。需要在 astream 循环结束后，检查是否已推送 output 和 completed，若没有则手动补充。
- **在推送每个节点数据时增加更详细的调试日志**：打印实际推送的 data 内容摘要

### 前端 Generate.vue 修改

- **修复早期三个卡片的空内容问题**：
  - 需求解析：确认 `data` 即为 UserRequirement 的 model_dump 结果（含 location/planned_load_kw/green_power_ratio）
  - 初稿生成：确认 `data.parsed` 含 green_power_result/cooling_result/power_supply_plan
  - 成本计算：确认 `data.economic_analysis_result` 或顶层含 total_capex_lakh/capex_breakdown
  - 在 handleSSENode 中增加 try-catch 包裹每个节点的处理逻辑，防止静默失败
  - 使用 `nextTick` 确保 Vue 响应式更新

- **修改专家评分格式**：
  - 将 `score: getMainScore(d.scores) * 5` 改为 `score: toNumber(d.confidence)` （0-1 小数）
  - 模板中 `{{ expert.score.toFixed(2) }} / 5.0` 改为 `{{ expert.score.toFixed(2) }}` 或 `{{ formatPercent(expert.score) }}`
  - 评分描述从"x / 5.0"改为"置信度: xx%"或直接显示小数

- **修复 90% 卡住问题**：
  - 增加 SSE 连接的超时检测和自动轮询降级机制：如果 SSE 在最后几个节点长时间无数据，主动轮询 `/api/workflow/status/{id}` 检测完成状态
  - 在 onmessage 中对 completed 信号做更强的容错处理

### 前端 Detail.vue 修改（确保方案详情正确展示）

- 确保从后端 solution 对象读取的数据字段完全对齐

## Impact
- Affected code: `src/greendatacenter/server.py`, `frontend/src/views/Generate.vue`, `frontend/src/views/Detail.vue`
- 不影响后端任何业务逻辑

## ADDED Requirements

### Requirement: 早期阶段卡片必须展示实时数据

#### Scenario: 需求解析卡片
- **WHEN** 收到 requirement_parser 节点的 SSE 数据
- **THEN** 卡片内必须显示：项目地点、总负荷(kW)、绿电目标(%)

#### Scenario: 初稿生成卡片
- **WHEN** 收到 draft_plan_agent 节点的 SSE 数据
- **THEN** 三张子卡片分别显示：光伏/风电/储能容量、制冷技术和PUE、供电Tier等级

#### Scenario: 成本计算卡片
- **WHEN** 收到 cost_calculation 节点的 SSE 数据
- **THEN** 卡片内必须显示：总投资、供电系统投资、绿电系统投资、是否超预算

### Requirement: 专家评分使用后端 confidence 格式

#### Scenario: 专家评分显示
- **WHEN** 收到专家分析节点的 SSE 数据
- **THEN** 评分以 0-1 小数形式展示（如 0.87），而非 x/5.0 格式

### Requirement: 工作流必须能到达 100% 完成

#### Scenario: 工作流全部节点执行完毕
- **WHEN** 后端所有节点（含 output）执行完毕
- **THEN** 前端进度条达到 100%，出现"查看方案详情"按钮

#### Scenario: SSE 断连降级
- **WHEN** SSE 连接在后端已完成但前端未收到 completed 信号
- **THEN** 前端通过轮询状态 API 检测到完成并自动跳转到完成状态

## MODIFIED Requirements

### Requirement: server.py _run_workflow 完整性保障

修改 `_run_workflow` 函数，在 `astream` 循环结束后：

```python
# astream 结束后的兜底逻辑
# 检查 output 节点是否已被推送
output_pushed = any(item.get("node") == "output" for item in workflows_store[workflow_id]["streaming_output"])
if not output_pushed:
    # 手动构造 output 节点的 SSE 消息
    output_msg = {"node": "output", "data": {"current_step": "completed", "final_solution": solution}, ...}
    if queue:
        await queue.put(output_msg)

# 发送 completed 信号
if queue:
    await queue.put({"node": "completed", "data": result})
```

### Requirement: Generate.vue 专家评分格式

修改前：
```
score: getMainScore(opinion.scores) * 5   // 如 4.25
模板: {{ score.toFixed(2) }} / 5.0        // 显示 "4.25 / 5.0"
```

修改后：
```
score: toNumber(opinion.confidence)         // 如 0.85
模板: {{ score.toFixed(2) }}                // 显示 "0.85"
```

### Requirement: Generate.vue 早期卡片数据容错

在每个节点的数据处理外层包裹 try-catch，确保单个节点解析失败不影响后续节点：
```javascript
try {
    // 节点特定处理逻辑
} catch (e) {
    console.error(`[SSE] Error processing ${nodeName}:`, e)
    addLog(`${nodeName}数据处理异常: ${e.message}`, 'error')
}
```
