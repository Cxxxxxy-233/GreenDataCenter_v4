# Checklist

- [ ] server.py astream 循环中打印每个事件的 node_name 和 node_output 顶层 keys
- [ ] server.py 能正确提取 draft_plan_agent 节点的 full_output（含 parsed.green_power_result 等）
- [ ] server.py 能正确提取 cost_calculation 节点的 full_output（含 total_capex_lakh 等）
- [ ] server.py 在 astream 结束后能补发所有未被推送的节点消息
- [ ] 前端初稿生成三卡片显示光伏/风电/储能容量、制冷方案、供电方案数据
- [ ] 前端成本计算卡片显示总投资/供电系统成本/绿电系统成本/是否超预算
- [ ] 前端编译无错误 (npm run build)
- [ ] 后端模块导入成功
