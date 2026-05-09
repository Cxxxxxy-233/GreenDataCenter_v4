# Checklist

- [x] server.py 的 `_run_workflow` 函数中，SSE 推送的 `data` 字段包含各节点 `streaming_output` 条目中的 `full_output` 内容（而非完整状态字典）
- [x] requirement_parser 节点的 SSE 数据能被前端正确解析，需求解析卡片显示地点/负荷/绿电目标
- [x] draft_plan_agent 节点的 SSE 数据能被前端正确解析，初稿生成三卡片显示光伏/风电/储能、制冷方案、供电方案
- [x] cost_calculation 节点的 SSE 数据能被前端正确解析，成本计算卡片显示总投资/分项成本/是否超预算
- [x] economic_analysis 节点的 SSE 数据能被前端正确解析，经济性专家卡片显示评分/摘要/建议
- [x] power_reliability_analysis 节点的 SSE 数据能被前端正确解析，可靠性专家卡片显示评分/摘要/建议
- [x] environmental_analysis 节点的 SSE 数据能被前端正确解析，环保性专家卡片显示评分/摘要/建议
- [x] debate_round 节点的 SSE 数据能被前端正确解析，辩论时间线按轮次展示发言
- [x] arbitrator 节点的 SSE 数据能被前端正确解析，仲裁决策卡片显示综合评分/三方评分/权衡方案
- [x] final_report 节点的 SSE 数据能被前端正确解析，报告预览区显示报告信息
- [x] output 节点完成后工作流能正常到达 100%，不卡在 90%
- [x] completed 信号能被前端正确接收，最终指标（PUE/绿电比例/总成本等）正确展示
- [x] 前端编译无错误（npm run build 成功）
