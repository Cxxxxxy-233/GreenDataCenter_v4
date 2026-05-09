# Checklist

- [x] server.py astream 循环中打印每个事件的 node_name 和 node_output 顶层 keys
- [x] server.py 记录所有在 streaming_output 中发现的节点名称
- [x] server.py 能正确提取 draft_plan_agent 节点的 full_output（含 parsed.green_power_result 等）
- [x] server.py 能正确提取 cost_calculation 节点的 full_output（含 total_capex_lakh 等）
- [x] server.py 在 astream 结束后能补发所有未被推送的节点消息
- [x] 前端初稿生成三卡片数据路径正确：data.parsed → green_power_result/cooling_result/power_supply_plan
- [x] 前端成本计算卡片数据路径正确：data.economic_analysis_result || data → total_capex_lakh/capex_breakdown
- [x] 前端编译无错误 (npm run build)
- [x] 后端模块导入成功
