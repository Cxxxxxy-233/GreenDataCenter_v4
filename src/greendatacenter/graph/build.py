"""
图构建模块
"""

from typing import Any

from langgraph.graph import StateGraph, END

from greendatacenter.memory import ExpertSharedMemory
from greendatacenter.graph.state import (
    GraphState,
    NODE_REQUIREMENT_PARSER,
    NODE_ECONOMIC_ANALYSIS,
    NODE_POWER_RELIABILITY_ANALYSIS,
    NODE_ENVIRONMENTAL_ANALYSIS,
    NODE_DEBATE_ROUND,
    NODE_ARBITRATOR,
    NODE_OUTPUT,
)
from greendatacenter.graph.nodes import (
    RequirementParserNode,
    EconomicAnalysisNode,
    PowerReliabilityAnalysisNode,
    EnvironmentalAnalysisNode,
    DebateRoundNode,
    ArbitratorNode,
    OutputNode,
)
from greendatacenter.graph.edges import check_debate_status


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
    economic_analysis_node = EconomicAnalysisNode(memory)
    power_reliability_analysis_node = PowerReliabilityAnalysisNode(memory)
    environmental_analysis_node = EnvironmentalAnalysisNode(memory)
    debate_round_node = DebateRoundNode(memory)
    arbitrator_node = ArbitratorNode(memory)
    output_node = OutputNode()

    # 添加节点到图
    graph.add_node(NODE_REQUIREMENT_PARSER, requirement_parser_node)
    graph.add_node(NODE_ECONOMIC_ANALYSIS, economic_analysis_node)
    graph.add_node(NODE_POWER_RELIABILITY_ANALYSIS, power_reliability_analysis_node)
    graph.add_node(NODE_ENVIRONMENTAL_ANALYSIS, environmental_analysis_node)
    graph.add_node(NODE_DEBATE_ROUND, debate_round_node)
    graph.add_node(NODE_ARBITRATOR, arbitrator_node)
    graph.add_node(NODE_OUTPUT, output_node)

    # 设置入口点
    graph.set_entry_point(NODE_REQUIREMENT_PARSER)

    # ===== 构建边 =====

    # 1. 需求解析 -> 顺序执行专家分析（避免输出交错）
    graph.add_edge(NODE_REQUIREMENT_PARSER, NODE_ECONOMIC_ANALYSIS)
    graph.add_edge(NODE_ECONOMIC_ANALYSIS, NODE_POWER_RELIABILITY_ANALYSIS)
    graph.add_edge(NODE_POWER_RELIABILITY_ANALYSIS, NODE_ENVIRONMENTAL_ANALYSIS)

    # 2. 所有专家分析完成 -> 辩论
    graph.add_edge(NODE_ENVIRONMENTAL_ANALYSIS, NODE_DEBATE_ROUND)

    # 3. 辩论循环 -> (继续辩论 或 结束辩论)
    graph.add_conditional_edges(
        NODE_DEBATE_ROUND,
        check_debate_status,
        {
            "continue": NODE_DEBATE_ROUND,  # 继续下一轮辩论
            "end": NODE_ARBITRATOR      # 结束辩论，进入仲裁
        }
    )

    # 4. 仲裁 -> 输出
    graph.add_edge(NODE_ARBITRATOR, NODE_OUTPUT)

    # 5. 输出 -> 结束
    graph.add_edge(NODE_OUTPUT, END)

    return graph
