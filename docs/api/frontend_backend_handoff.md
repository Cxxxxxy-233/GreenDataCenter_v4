# 前后端对接文档

## 1. 文档目的

本文档用于把当前项目中已经实现的后端工作流接口，转换成可直接用于前端联调的页面对接说明，重点回答 4 个问题：

1. 每个前端页面应该调用哪个后端接口
2. 每个页面应该使用哪些返回字段
3. 哪些前端字段当前虽然提交了，但后端实际上没有真正生效
4. 哪些页面行为当前仍是 mock，或与后端真实实现存在差异

本文档基于当前代码仓库中的真实实现整理，优先级以 `server.py`、`nodes.py`、`state.py` 和前端各页面源码为准。

---

## 2. 后端真实接口总览

后端当前已经实现的 HTTP 接口如下：

| 接口 | 方法 | 用途 | 前端是否应直接使用 |
| --- | --- | --- | --- |
| `/api/workflow/start` | `POST` | 启动一次完整方案生成工作流 | 是 |
| `/api/workflow/stream/{workflow_id}` | `GET` | 通过 SSE 订阅工作流流式输出 | 是 |
| `/api/workflow/status/{workflow_id}` | `GET` | 查询工作流状态 | 是，作为兜底轮询 |
| `/api/requirements` | `GET` | 查看内存中的需求列表 | 否，当前前端可不接 |
| `/api/requirements/{req_id}` | `GET` | 查看单个需求 | 否，当前前端可不接 |
| `/api/solutions` | `GET` | 查看已生成方案列表 | 是 |
| `/api/solutions/{solution_id}` | `GET` | 查看单个方案详情 | 是 |
| `/api/solutions/{solution_id}/export/markdown` | `GET` | 导出 Markdown 报告文本 | 是 |
| `/api/system/status` | `GET` | 查看系统状态 | 可选 |

当前后端没有实现的接口：

| 接口 | 说明 |
| --- | --- |
| `POST /api/requirements` | 前端现在不需要单独先提需求再启动工作流 |
| `DELETE /api/solutions/{id}` | 首页、历史页的删除按钮目前没有真实后端接口支撑 |
| `PUT /api/solutions/{id}` | 没有方案编辑保存接口 |
| `POST /api/solutions/{id}/copy` | 没有方案复制接口 |

---

## 3. 统一数据流

当前建议前端按下面这条真实链路接后端：

1. 在 `/config` 收集参数
2. 调用 `POST /api/workflow/start`
3. 拿到 `workflow_id`
4. 在 `/generate` 通过 `GET /api/workflow/stream/{workflow_id}` 监听各节点流式输出
5. 工作流完成后，使用同一个 `workflow_id` 作为 `solution_id`
6. 在 `/detail/:id` 调用 `GET /api/solutions/{id}` 读取最终详情
7. 历史列表和首页最近项目统一调用 `GET /api/solutions`

注意：

- 当前后端将 `workflow_id` 直接作为 `solution_id` 存入 `solutions_store`
- 因此前端不需要额外转换 ID
- `/generate` 页建议把 `workflow_id` 保存在 `localStorage.currentWorkflowId`
- 工作流完成后可把同一个值保存为 `currentSolutionId`

---

## 4. 页面级对接说明

### 4.1 首页 `/`

**页面职责**

- 展示平台概览统计
- 展示最近项目
- 跳转到配置页或详情页

**应调用接口**

- `GET /api/solutions`

**字段映射**

| 首页展示项 | 后端字段 | 说明 |
| --- | --- | --- |
| 最近项目 `id` | `solution.id` | 用于跳转 `/detail/:id` |
| 项目名称 | `solution.name` | 若为空可兜底为“未命名方案” |
| 创建时间 | `solution.created_at` | 需要前端格式化 |
| 状态 | `solution.success` | `true -> 已完成`，否则 `失败` |
| PUE | `solution.key_metrics.pue` | 详情页和首页保持一致 |
| 绿电率 | `solution.key_metrics.green_power_ratio` | 前端展示时乘 `100` |
| 总投资 | `solution.key_metrics.total_cost` 或成本节点重算值 | 首页可先用 `key_metrics.total_cost` |

**建议派生统计**

| 统计卡片 | 建议来源 |
| --- | --- |
| 累计生成方案 | `solutions.length` |
| 平均生成耗时 | `solution.generation_time` 的平均值 |
| 平均 PUE | `solution.key_metrics.pue` 的平均值 |
| 平均绿电消纳 | `solution.key_metrics.green_power_ratio` 的平均值后转百分比 |

**当前差异**

- `frontend/src/api/index.js` 中 `solutionApi.getAll()` 仍返回 `mockSolutionsList`
- `Home.vue` 当前的 `location` 字段被写死为 `--`
- 如果要显示真实地点，后端 `GET /api/solutions` 当前摘要列表未直接带 `requirement.location`，需要前端额外进详情页读取，或后端在列表接口中补出 `requirement` 摘要
- “查看示例方案”现在跳转 `/detail/mock-solution-001`，这依赖 mock 数据，不适合真实环境

---

### 4.2 工作流介绍页 `/workflow`

**页面职责**

- 展示多智能体工作流结构说明
- 作为静态说明页，帮助用户理解流程

**应调用接口**

- 当前可以不调用业务接口
- 如需展示“系统已就绪/模型可用/图节点数”等状态，可选接 `GET /api/system/status`

**字段映射建议**

| 页面内容 | 后端来源 |
| --- | --- |
| 工作流节点顺序 | 固定写死即可，来源于 `build.py` |
| 最大辩论轮次 | `GraphState.max_debate_rounds` 默认值 |
| 系统状态 | `/api/system/status.status` |

**当前差异**

- 该页基本是静态说明页，不依赖 mock 方案数据
- “开始方案生成”按钮目前只跳转到 `/generate`，更合理的方式是跳转 `/config`

---

### 4.3 参数配置页 `/config`

**页面职责**

- 收集用户输入参数
- 发起工作流

**应调用接口**

- `POST /api/workflow/start`

**请求体字段**

后端 `WorkflowStartRequest` 当前接收以下字段：

| 字段 | 必填 | 前端来源 | 说明 |
| --- | --- | --- | --- |
| `location` | 是 | `formData.location` | 城市名，直接传中文 |
| `planned_load_kw` | 是 | `formData.planned_load_kw` | 总负荷 |
| `green_power_ratio` | 是 | `formData.green_power_ratio / 100` | 前端百分比需转为 `0-1` |
| `planned_area` | 是 | `formData.planned_area` | 建筑面积 |
| `budget_constraint` | 是 | `formData.budget_constraint` | 预算上限 |
| `cooling_technology` | 否 | `formData.cooling_technology` | 当前后端接收，但未真实传到制冷工具 |
| `machine_room_grade` | 否 | `formData.machine_room_grade` | 会影响供电方案 |
| `pue_target` | 否 | `formData.pue_target` | 会影响供电和制冷 |
| `sim_hours` | 否 | `formData.sim_hours` | 会影响绿电优化 |
| `year` | 否 | `formData.year` | 接口接收，但下游绿电工具实际未透传 |
| `date` | 否 | `formData.date` | 接口接收，但当前未透传到绿电工具 |
| `pv_tilt` | 否 | `formData.pv_tilt` | 接口接收，但当前未透传 |
| `pv_azimuth` | 否 | `formData.pv_azimuth` | 接口接收，但当前未透传 |
| `wind_cut_in_ms` | 否 | `formData.wind_cut_in_ms` | 接口接收，但当前未透传 |
| `wind_rated_ms` | 否 | `formData.wind_rated_ms` | 接口接收，但当前未透传 |
| `wind_cut_out_ms` | 否 | `formData.wind_cut_out_ms` | 接口接收，但当前未透传 |
| `computing_power_density` | 否 | `formData.computing_power_density` | 会影响制冷计算 |
| `carbon_emission_factor` | 否 | `formData.carbon_emission_factor` | 当前主要作为上下文使用 |
| `electricity_prices` | 否 | `formData.electricity_prices` | 当前主要作为上下文使用 |
| `maxiter` | 否 | `formData.maxiter` | 接口接收，但当前未透传 |
| `popsize` | 否 | `formData.popsize` | 接口接收，但当前未透传 |
| `seed` | 否 | `formData.seed` | 接口接收，但当前未透传 |

**成功返回**

```json
{
  "workflow_id": "wf_xxx",
  "requirement_id": "req_xxx"
}
```

**前端处理建议**

| 动作 | 建议 |
| --- | --- |
| 保存工作流 ID | `localStorage.currentWorkflowId = workflow_id` |
| 保存配置快照 | `localStorage.projectConfig` |
| 页面跳转 | 成功后跳转 `/generate` |

**当前差异**

- `Config.vue` 已经正确把 `green_power_ratio` 从百分比转成小数，这一点可以保留
- `Config.vue` 当前按钮文案是“下一步：生成方案”，但实际已经直接启动了工作流
- `cooling_technology` 虽然已提交，但当前 `draft_plan_agent` 调制冷工具时并没有传这个字段，因此用户选择的制冷技术当前不会真正控制后端结果

---

### 4.4 方案生成页 `/generate`

**页面职责**

- 展示工作流执行进度
- 实时展示节点产出
- 在完成后跳转详情页

**应调用接口**

- 主通道：`GET /api/workflow/stream/{workflow_id}`
- 兜底通道：`GET /api/workflow/status/{workflow_id}`

**流式消息结构**

后端 SSE 每条消息统一为：

```json
{
  "node": "requirement_parser",
  "data": {
    "content": "需求解析完成",
    "full_output": {},
    "timestamp": "..."
  },
  "timestamp": "..."
}
```

实际前端应重点使用 `node` 和 `data.full_output`。

**节点与页面模块映射**

| 生成页模块 | 对应后端节点 | 主要字段 |
| --- | --- | --- |
| 需求解析卡片 | `requirement_parser` | `full_output.location`、`planned_load_kw`、`green_power_ratio` |
| 初稿生成面板 | `draft_plan_agent` | `full_output.green_power_result`、`cooling_result`、`power_supply_plan` |
| 成本计算面板 | `cost_calculation` | `full_output.economic_analysis_result` |
| 经济专家卡片 | `economic_analysis` | `full_output.summary`、`scores`、`metrics`、`recommendations` |
| 可靠性专家卡片 | `power_reliability_analysis` | 同上 |
| 环保专家卡片 | `environmental_analysis` | 同上 |
| 辩论面板 | `debate_round` | `speaker`、`content`、`round` 或汇总字段 |
| 仲裁面板 | `arbitrator` | `full_output.summary`、`overall_scores`、`key_metrics`、`trade_offs`、`risks` |
| 报告面板 | `final_report` | `full_output.path` |
| 完成面板 | `output` / `completed` | 最终完成状态 |

**推荐前端状态结构**

| 前端状态 | 来源 |
| --- | --- |
| `currentNodeIndex` | 根据最新 `node` 推导 |
| `completedNodes` | 已收到的节点集合 |
| `nodeResults.requirementParser` | `requirement_parser.full_output` |
| `nodeResults.draftPlan` | `draft_plan_agent.full_output` |
| `nodeResults.costCalculation` | `cost_calculation.full_output.economic_analysis_result` |
| `expertResults` | 三个专家节点的 `full_output` |
| `debateResults` | 所有 `debate_round` 事件聚合 |
| `arbitratorResult` | `arbitrator.full_output` |
| `finalReport` | `final_report.full_output` |

**状态查询接口返回**

`GET /api/workflow/status/{workflow_id}` 返回：

```json
{
  "workflow_id": "...",
  "status": "pending|running|completed|failed",
  "requirement_id": "...",
  "has_result": true,
  "error": null
}
```

**当前差异**

- `Generate.vue` 现在整个页面仍基于 `mockSolutionData` 和定时器推进，不是真实后端数据
- `workflowApi.connectStream()` 当前返回 `null`
- 页面中很多“生成过程说明”是静态说明文案，可保留，但底层数据应切换到真实 SSE
- 成本面板当前通过 mock 数据把“制冷成本”并入总投资，这个展示逻辑可以保留，但应以真实 `cost_calculation` 和 `draft_plan_agent.cooling_result.economic_indicators` 为数据源

---

### 4.5 方案详情页 `/detail/:id`

**页面职责**

- 展示最终方案详情
- 展示中间结果、专家意见、报告文本

**应调用接口**

- `GET /api/solutions/{solution_id}`
- 可选：`GET /api/solutions/{solution_id}/export/markdown`

**详情接口返回结构**

当前后端返回：

```json
{
  "id": "wf_xxx",
  "debate_history": [],
  "intermediate_results": {},
  "...solution_fields": "..."
}
```

其中：

- 顶层大部分字段来自最终 `solution`
- `intermediate_results` 按节点名聚合各节点 `full_output`
- `debate_history` 试图从流式记录提取辩论消息

**字段映射**

| 详情页模块 | 后端字段 |
| --- | --- |
| 概览标题 | `solution.name` |
| 方案摘要 | `solution.summary` |
| 综合评分 | `solution.overall_scores` |
| 关键指标 | `solution.key_metrics` |
| 关键权衡 | `solution.trade_offs` |
| 风险列表 | `solution.risks` |
| 最终建议 | `solution.recommendations` |
| 置信度 | `solution.confidence` |
| 制冷详情 | `intermediate_results.draft_plan_agent.full_output.cooling_result` |
| 绿电详情 | `intermediate_results.draft_plan_agent.full_output.green_power_result.optimization` |
| 供电详情 | `intermediate_results.draft_plan_agent.full_output.power_supply_plan` |
| 成本详情 | `intermediate_results.cost_calculation.full_output.economic_analysis_result` |
| 经济专家 | `intermediate_results.economic_analysis.full_output` |
| 可靠性专家 | `intermediate_results.power_reliability_analysis.full_output` |
| 环保专家 | `intermediate_results.environmental_analysis.full_output` |
| 仲裁结果 | `intermediate_results.arbitrator.full_output` 或顶层 `solution` |
| 报告路径 | `intermediate_results.final_report.full_output.path` |
| Markdown 文本 | `solution.final_report` |

**导出接口返回结构**

```json
{
  "content": "markdown文本",
  "filename": "report_xxx.md"
}
```

**当前差异**

- `Detail.vue` 已经按“顶层 solution + intermediate_results”双路兜底写了很多兼容逻辑，这部分思路是对的
- 但当前 `solutionApi.getById()` 仍返回 `mockSolutionData`
- 后端 `GET /api/solutions/{id}` 中 `debate_history` 的提取条件写成了 `node == "debate"`，而真实节点名是 `debate_round`，所以当前这个字段很可能为空
- 后端 `final_report` 节点流式结果只放了 `path`，真正 Markdown 正文仍主要依赖最终 `solution.final_report`

---

### 4.6 历史项目页 `/history`

**页面职责**

- 展示全部方案列表
- 提供筛选、排序、跳转详情

**应调用接口**

- `GET /api/solutions`

**字段映射**

| 历史页字段 | 后端字段 | 备注 |
| --- | --- | --- |
| `id` | `solution.id` | 详情跳转用 |
| `name` | `solution.name` | 列表标题 |
| `createTime` | `solution.created_at` | 需格式化 |
| `status` | `solution.success` | 仅能区分“已完成/失败” |
| `pue` | `solution.key_metrics.pue` | 可直接展示 |
| `greenRate` | `solution.key_metrics.green_power_ratio * 100` | 百分比显示 |
| `investment` | `solution.key_metrics.total_cost` | 若需更准确投资口径，建议从详情取成本节点结果 |
| `cabinetPower` | 当前无稳定直接字段 | 建议改为 `computing_power_density`，但列表接口未直接提供 |

**当前差异**

- `History.vue` 现在的删除、批量删除、复制项目都是纯前端行为
- 后端没有删除接口，所以真实联调时按钮要么隐藏，要么改成“仅本地移除显示”
- “编辑参数”现在直接跳转 `/config`，但后端也没有读取旧方案回填到配置页的接口

---

### 4.7 设置页 `/settings` 与帮助页 `/help`

**页面职责**

- 当前属于静态页面

**应调用接口**

- 当前可不接业务接口
- 如需展示系统运行状态，可选接 `GET /api/system/status`

---

## 5. 关键请求与响应字段

### 5.1 启动工作流请求体

推荐以前端当前 `Config.vue` 的转换结果为准：

```json
{
  "location": "乌兰察布",
  "planned_load_kw": 12000,
  "green_power_ratio": 0.95,
  "planned_area": 18000,
  "budget_constraint": 35000,
  "cooling_technology": "浸没式液冷",
  "machine_room_grade": "A+",
  "pue_target": 1.18,
  "sim_hours": 168,
  "year": 2025,
  "date": "2025-07-01",
  "pv_tilt": null,
  "pv_azimuth": 180,
  "wind_cut_in_ms": 3.0,
  "wind_rated_ms": 12.0,
  "wind_cut_out_ms": 25.0,
  "computing_power_density": 30,
  "carbon_emission_factor": 0.5,
  "electricity_prices": {
    "尖峰电价": 0.5,
    "高峰电价": 0.4,
    "平段电价": 0.3,
    "低谷电价": 0.25,
    "深谷电价": 0.2
  },
  "maxiter": 60,
  "popsize": 10,
  "seed": 42
}
```

### 5.2 `draft_plan_agent` 关键输出

```json
{
  "green_power_result": {},
  "cooling_result": {},
  "power_supply_plan": {},
  "raw_output": "...",
  "parsed": {
    "green_power_result": {},
    "cooling_result": {},
    "power_supply_plan": {}
  }
}
```

前端优先读取：

- `green_power_result.optimization`
- `cooling_result`
- `power_supply_plan`

### 5.3 `cost_calculation` 关键输出

```json
{
  "economic_analysis_result": {
    "budget_constraint_lakh": 35000,
    "total_capex_lakh": 29800,
    "budget_delta_lakh": 5200,
    "is_over_budget": false,
    "capex_breakdown": {
      "power_supply_system_lakh": 3000,
      "green_power_system_lakh": 24000,
      "details": {}
    }
  }
}
```

### 5.4 专家节点统一输出

三位专家都遵循相同结构：

```json
{
  "expert_type": "economic",
  "expert_name": "Economic Analysis Expert-Zhang",
  "summary": "...",
  "reasoning": "...",
  "scores": {},
  "metrics": {},
  "recommendations": [],
  "concerns": [],
  "confidence": 0.86
}
```

### 5.5 仲裁节点最终输出

```json
{
  "name": "方案名称",
  "summary": "最终摘要",
  "overall_scores": {},
  "key_metrics": {},
  "economic_section": {},
  "power_reliability_section": {},
  "environmental_section": {},
  "trade_offs": [],
  "risks": [],
  "recommendations": [],
  "confidence": 0.9
}
```

---

## 6. 当前“提交了但没真正生效”的字段

下面这些字段在前端表单中存在、后端接口也接收，但当前下游工具链没有真正使用，或没有按前端期望那样生效。

| 字段 | 当前状态 | 原因 |
| --- | --- | --- |
| `cooling_technology` | 未真正生效 | 制冷工具调用时没有把该字段传入 |
| `pv_tilt` | 未真正生效 | 绿电工具调用时未透传 |
| `pv_azimuth` | 未真正生效 | 绿电工具调用时未透传 |
| `wind_cut_in_ms` | 未真正生效 | 绿电工具调用时未透传 |
| `wind_rated_ms` | 未真正生效 | 绿电工具调用时未透传 |
| `wind_cut_out_ms` | 未真正生效 | 绿电工具调用时未透传 |
| `maxiter` | 未真正生效 | 绿电工具调用时未透传 |
| `popsize` | 未真正生效 | 绿电工具调用时未透传 |
| `seed` | 未真正生效 | 绿电工具调用时未透传 |
| `date` | 未真正生效 | 绿电工具调用时未透传 |
| `year` | 部分失效 | 节点中实际写死传 `2025` |
| `planned_area` | 仅弱生效 | 当前主要进入需求上下文，没有明确工具计算使用 |
| `carbon_emission_factor` | 仅弱生效 | 主要作为 LLM 上下文，不走确定性计算 |
| `electricity_prices` | 仅弱生效 | 当前主要作为 LLM 上下文，不走确定性计算 |

真正明确会影响下游计算的字段如下：

| 字段 | 实际影响链路 |
| --- | --- |
| `location` | 绿电工具、需求上下文 |
| `planned_load_kw` | 绿电工具、制冷工具、供电工具 |
| `green_power_ratio` | 绿电工具、制冷工具、专家分析 |
| `machine_room_grade` | 供电工具 |
| `pue_target` | 制冷工具、供电工具 |
| `sim_hours` | 绿电工具 |
| `budget_constraint` | 成本节点 |
| `computing_power_density` | 制冷工具 |

---

## 7. 当前前端中的 mock 位置

以下文件目前仍主要依赖 mock：

| 文件 | 当前状态 |
| --- | --- |
| `frontend/src/api/index.js` | 所有 API 方法都被 mock Promise 替代 |
| `frontend/src/views/Generate.vue` | 全流程基于 `mockSolutionData` 和定时器推进 |
| `frontend/src/views/Detail.vue` | 结构已接近真实后端，但数据源仍是 mock |
| `frontend/src/views/Home.vue` | 列表结构接近真实，但数据来自 mock API |
| `frontend/src/views/History.vue` | 列表结构接近真实，但数据来自 mock API |

因此，联调的第一优先级不是改页面样式，而是：

1. 打开真实 axios 实例
2. 恢复真实 `BASE_URL`
3. 让 `workflowApi.connectStream()` 返回真实 `EventSource`
4. 把 `Generate.vue` 的 mock 定时流程替换为 SSE 驱动

---

## 8. 页面改造优先级建议

### 第一优先级

- `frontend/src/api/index.js`
- `frontend/src/views/Config.vue`
- `frontend/src/views/Generate.vue`

原因：

- 这三处决定“能不能真正发起工作流并看到实时结果”

### 第二优先级

- `frontend/src/views/Detail.vue`
- `frontend/src/views/History.vue`
- `frontend/src/views/Home.vue`

原因：

- 这三处决定“能不能正确展示后端结果”

### 第三优先级

- `frontend/src/views/Workflow.vue`
- `frontend/src/views/Settings.vue`
- `frontend/src/views/Help.vue`

原因：

- 这几页不影响主联调链路

---

## 9. 联调时的已知缺口

当前如果开始真实前后端联调，需要特别注意下面几个缺口：

1. 前端删除、复制、编辑旧项目都没有真实后端接口支撑
2. `GET /api/solutions` 列表接口没有直接带出需求地点、功率密度等摘要字段，列表页展示会受限
3. `debate_history` 当前后端提取逻辑可能为空，因为节点名过滤条件不一致
4. `cooling_technology` 等高级参数虽然有表单，但暂时不会真实影响后端方案
5. 绿电高级参数未透传，前端即使开放配置，也无法体现到结果上

---

## 10. 推荐的前端联调顺序

建议按以下顺序推进：

1. 先打通 `/config -> /generate -> /detail/:id` 主链路
2. 再接 `/history` 的真实列表
3. 再接首页统计与最近项目
4. 最后处理删除、复制、编辑回填等扩展功能

如果只做最小可用联调，最少只需要完成以下能力：

1. `POST /api/workflow/start`
2. `GET /api/workflow/stream/{workflow_id}`
3. `GET /api/solutions/{solution_id}`

做到这三步，整个系统就已经能从“全 mock 演示”进入“真实后端驱动”状态。
