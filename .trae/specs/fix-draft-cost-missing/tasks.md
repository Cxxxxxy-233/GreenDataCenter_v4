# Tasks

- [ ] Task 1: 修改 server.py 的 astream 数据提取和补发逻辑
  - [ ] 在 astream 循环中增加日志：打印每个事件的 node_name 和 node_output 的顶层 keys
  - [ ] 修改第二层查找逻辑：从 node_output["streaming_output"] 中不仅查找当前节点，还记录所有发现的节点
  - [ ] 在 astream 循环结束后，对比节点追加的 streaming_output 和已推送的节点列表，补发所有缺失节点的 SSE 消息（特别是 draft_plan_agent 和 cost_calculation）

- [ ] Task 2: 验证前端数据路径正确性
  - [ ] 确认 handleSSENode 中 draft_plan_agent 的 data.parsed 路径能正确读取 green_power_result/cooling_result/power_supply_plan
  - [ ] 确认 handleSSENode 中 cost_calculation 的 data.economic_analysis_result 或 data 顶层能正确读取 total_capex_lakh/capex_breakdown

- [ ] Task 3: 编译验证
  - [ ] 前端 npm run build 通过
  - [ ] 后端模块导入成功

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1, Task 2]
