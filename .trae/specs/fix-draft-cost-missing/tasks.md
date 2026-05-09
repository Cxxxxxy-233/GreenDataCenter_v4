# Tasks

- [x] Task 1: 修改 server.py 的 astream 数据提取和补发逻辑
  - [x] 在 astream 循环中增加日志：打印每个事件的 node_name 和 node_output 的顶层 keys（`[ASTREAM] node=xxx, output_keys=[...]`）
  - [x] 记录所有在 node_output.streaming_output 中发现的节点名称到 `all_node_names_from_so` 集合
  - [x] 保存最后一个包含 streaming_output 的 node_output 到 `last_node_output_with_so`
  - [x] 在 astream 循环结束后，计算 `missing_nodes = all_node_names_from_so - pushed_nodes`
  - [x] 从 `last_node_output_with_so["streaming_output"]` 中补发所有缺失节点的 SSE 消息，每条消息包含该节点的 full_output

- [x] Task 2: 验证前端数据路径正确性
  - [x] draft_plan_agent: server推送 `{raw_output, parsed}` → 前端 `data.parsed.green_power_result` ✅
  - [x] cost_calculation: server推送 `analysis_result` → 前端 `d.economic_analysis_result || d` 回退 ✅

- [x] Task 3: 编译验证
  - [x] 前端 npm run build 通过
  - [x] 后端模块导入成功

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1, Task 2]
