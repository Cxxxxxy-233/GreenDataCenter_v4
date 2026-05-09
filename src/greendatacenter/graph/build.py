"""
图构建模块
"""

from typing import Any

from langgraph.graph import StateGraph, END

from greendatacenter.memory import ExpertSharedMemory
from greendatacenter.graph.state import (
    GraphState,
    NODE_REQUIREMENT_PARSER,
    NODE_DRAFT_PLAN_AGENT,
    NODE_COST_CALCULATION,
    NODE_ECONOMIC_ANALYSIS,
    NODE_POWER_RELIABILITY_ANALYSIS,
    NODE_ENVIRONMENTAL_ANALYSIS,
    NODE_DEBATE_ROUND,
    NODE_ARBITRATOR,
    NODE_FINAL_REPORT,
    NODE_OUTPUT,
)
from greendatacenter.graph.nodes import (
    RequirementParserNode,
    DraftPlanAgentNode,
    CostCalculationNode,
    EconomicAnalysisNode,
    PowerReliabilityAnalysisNode,
    EnvironmentalAnalysisNode,
    DebateRoundNode,
    ArbitratorNode,
    FinalReportNode,
    OutputNode,
)
from greendatacenter.graph.edges import check_debate_status, check_budget_status


def build_data_center_graph(memory: ExpertSharedMemory) -> StateGraph:
    """
    构建数据中心建设方案生成图

    Args:
        memory: 共享记忆

    Returns:
        构建好的StateGraph
    """
    # 创建图
    graph = StateGraph(GraphState)

    # 创建节点
    requirement_parser_node = RequirementParserNode(memory)
    draft_plan_agent_node = DraftPlanAgentNode(memory)
    cost_calculation_node = CostCalculationNode()
    economic_analysis_node = EconomicAnalysisNode(memory)
    power_reliability_analysis_node = PowerReliabilityAnalysisNode(memory)
    environmental_analysis_node = EnvironmentalAnalysisNode(memory)
    debate_round_node = DebateRoundNode(memory)
    arbitrator_node = ArbitratorNode(memory)
    final_report_node = FinalReportNode()
    output_node = OutputNode()

    # 添加节点到图
    graph.add_node(NODE_REQUIREMENT_PARSER, requirement_parser_node)
    graph.add_node(NODE_DRAFT_PLAN_AGENT, draft_plan_agent_node)
    graph.add_node(NODE_COST_CALCULATION, cost_calculation_node)
    graph.add_node(NODE_ECONOMIC_ANALYSIS, economic_analysis_node)
    graph.add_node(NODE_POWER_RELIABILITY_ANALYSIS, power_reliability_analysis_node)
    graph.add_node(NODE_ENVIRONMENTAL_ANALYSIS, environmental_analysis_node)
    graph.add_node(NODE_DEBATE_ROUND, debate_round_node)
    graph.add_node(NODE_ARBITRATOR, arbitrator_node)
    graph.add_node(NODE_FINAL_REPORT, final_report_node)
    graph.add_node(NODE_OUTPUT, output_node)

    # 设置入口点
    graph.set_entry_point(NODE_REQUIREMENT_PARSER)

    # ===== 构建边 =====

    # 1. 需求解析 -> 初稿生成专家
    graph.add_edge(NODE_REQUIREMENT_PARSER, NODE_DRAFT_PLAN_AGENT)
    graph.add_edge(NODE_DRAFT_PLAN_AGENT, NODE_COST_CALCULATION)

    # 2. 成本计算 -> (预算重试 或 专家分析)
    graph.add_conditional_edges(
        NODE_COST_CALCULATION,
        check_budget_status,
        {
            "retry": NODE_DRAFT_PLAN_AGENT,
            "continue": NODE_ECONOMIC_ANALYSIS,
        },
    )

    # 3. 顺序执行专家分析（避免输出交错）
    graph.add_edge(NODE_ECONOMIC_ANALYSIS, NODE_POWER_RELIABILITY_ANALYSIS)
    graph.add_edge(NODE_POWER_RELIABILITY_ANALYSIS, NODE_ENVIRONMENTAL_ANALYSIS)

    # 4. 所有专家分析完成 -> 辩论
    graph.add_edge(NODE_ENVIRONMENTAL_ANALYSIS, NODE_DEBATE_ROUND)

    # 5. 辩论循环 -> (继续辩论 或 结束辩论)
    graph.add_conditional_edges(
        NODE_DEBATE_ROUND,
        check_debate_status,
        {
            "revise": NODE_DRAFT_PLAN_AGENT,
            "end": NODE_ARBITRATOR
        }
    )

    # 6. 仲裁 -> 最终报告
    graph.add_edge(NODE_ARBITRATOR, NODE_FINAL_REPORT)

    # 7. 最终报告 -> 输出
    graph.add_edge(NODE_FINAL_REPORT, NODE_OUTPUT)

    # 5. 输出 -> 结束
    graph.add_edge(NODE_OUTPUT, END)

    return graph
