# Tasks

- [x] Task 1: 修改 server.py 的 SSE 数据推送逻辑
  - [x] 修改 `_run_workflow` 函数中 `astream` 循环内的数据推送逻辑：从节点返回的完整状态字典中，提取各节点自行追加到 `streaming_output` 的结构化条目（含 `full_output` 字段）作为 SSE 推送的 `data`
  - [x] 确保 output 节点的数据也被正确捕获和推送（fallback 到原始 node_output）
  - [x] 在推送前添加日志打印实际推送的数据结构，便于调试

- [x] Task 2: 重写 Generate.vue handleSSENode 函数的数据映射
  - [x] requirement_parser 节点：修正数据路径为 `data.requirement || d`（兼容两种格式）
  - [x] draft_plan_agent 节点：保持从 `data.parsed` 读取，增加调试日志
  - [x] cost_calculation 节点：修正为 `data.economic_analysis_result || d` 兼容读取
  - [x] economic_analysis / power_reliability_analysis / environmental_analysis 节点：修正为 `data.economic_opinion / power_reliability_opinion / environmental_opinion || d`
  - [x] arbitrator 节点：修正为 `data.solution || d` 读取仲裁结果
  - [x] final_report 节点：修正为 `data.solution || d` 多层回退读取报告路径
  - [x] debate_round 节点：确保辩论消息格式正确解析
  - [x] 新增 output 节点处理

- [x] Task 3: 修复工作流卡在90%的问题
  - [x] 检查并确保 output 节点完成后正确发送 completed 信号
  - [x] 增强 SSE 断线重连逻辑（增加重连次数限制 MAX_SSE_RECONNECTS=5）
  - [x] 添加超时保护机制（120秒无数据警告）

- [x] Task 4: 端到端验证
  - [x] 前端编译通过 (npm run build 成功)
  - [x] 后端模块导入成功 (from greendatacenter.server import app)

# Task Dependencies
- [Task 2] depends on [Task 1] (前端映射需匹配后端推送格式)
- [Task 4] depends on [Task 1, Task 2, Task 3]
