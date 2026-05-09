# Tasks

- [x] Task 1: 修复 server.py 的 output 节点丢失和 completed 信号问题
  - [x] 在 `_run_workflow` 函数的 `astream` 循环结束后，检查是否已推送 "output" 节点的消息
  - [x] 若未推送，手动构造并推送 output 节点的 SSE 消息（包含 final_solution 数据）
  - [x] 确保 completed 信号在 astream 结束后始终被推送到 SSE 队列

- [x] Task 2: 修复 Generate.vue 早期卡片空内容问题
  - [x] 在 handleSSENode 中为 requirement_parser/draft_plan_agent/cost_calculation 三个节点增加 try-catch 错误捕获和 console.log 详细日志
  - [x] 确认 requirement_parser 的数据路径：server.py 推送的 data 应为 UserRequirement.model_dump()（直接包含 location/planned_load_kw/green_power_ratio）
  - [x] 确认 draft_plan_agent 的数据路径：data 应含 parsed 字段或顶层 green_power_result/cooling_result/power_supply_plan
  - [x] 确认 cost_calculation 的数据路径：data 应含 economic_analysis_result 或顶层 total_capex_lakh/capex_breakdown

- [x] Task 3: 修改专家评分为 confidence 格式
  - [x] 将三位专家的 score 计算从 `getMainScore(d.scores) * 5` 改为 `toNumber(d.confidence)`
  - [x] 将模板中专家评分显示从 `x / 5.0` 改为小数格式（如 `0.87`），标签改为"置信度"

- [x] Task 4: 增加 SSE 断连降级机制
  - [x] 当 SSE 长时间无数据且进度 >= 80% 时，启动轮询 `/api/workflow/status/{id}` 作为降级方案
  - [x] 轮询检测到 status=completed 时，自动设置 isCompleted=true、progressPercent=100、展示最终数据并加载方案详情

- [x] Task 5: 端到端验证
  - [x] 前端编译通过 (npm run build)
  - [x] 后端模块导入成功 (from greendatacenter.server import app)

# Task Dependencies
- [Task 2, Task 3] 可并行执行
- [Task 4] depends on [Task 1] (降级需要后端 status API 正常工作)
- [Task 5] depends on [Task 1, Task 2, Task 3, Task 4]
