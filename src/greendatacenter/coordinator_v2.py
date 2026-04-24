# -*- coding: utf-8 -*-
"""
AI系统协调器（基于LangGraph）
"""

import json
import sys
from datetime import datetime
from typing import Any, Optional

from langgraph.graph import StateGraph

from greendatacenter.memory import ExpertSharedMemory
from greendatacenter.graph.build import build_data_center_graph
from greendatacenter.graph.state import GraphState

# 强制UTF-8输出（仅在交互式控制台模式下）
# 这个会影响终端输出不要解开注释
# if sys.platform == "win32" and sys.stdout.isatty():
#     import io
#     sys.stdout = io.TextIOWrapper(sys.stdout, encoding="utf-8")
#     sys.stderr = io.TextIOWrapper(sys.stderr, encoding="utf-8")


class AISystemCoordinator:
    """AI系统协调器"""

    def __init__(self):
        """初始化AI系统协调器"""
        # 创建共享记忆
        self.memory = ExpertSharedMemory()

        # 构建图
        self.graph = build_data_center_graph(self.memory)

        # 编译图
        self.compiled_graph = self.graph.compile()

        print("AI系统协调器初始化完成")
        print(f"图节点: {list(self.graph.nodes.keys())}")

    async def generate_solution_async(
        self,
        input_data: dict[str, Any],
        on_stream_chunk: Optional[callable] = None
    ) -> dict[str, Any]:
        """
        异步生成数据中心建设方案

        Args:
            input_data: 用户输入的需求数据
            on_stream_chunk: 流式输出回调函数

        Returns:
            包含方案和流式输出的字典
        """
        start_time = datetime.now()

        print("\n" + "="*70)
        print("开始生成数据中心建设方案")
        print("="*70)

        # 初始化状态
        initial_state: GraphState = {
            "requirement": input_data,
            "user_id": "user_" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "current_step": "start",
            "next_step": "",
            "debate_round": 1,
            "max_debate_rounds": 5,
            "consensus_reached": False,
            "should_continue_debate": True,
            "economic_opinion": None,
            "power_reliability_opinion": None,
            "environmental_opinion": None,
            "debate_history": [],
            "consensus_score": 0.0,
            "solution": {},
            "streaming_output": []
        }

        try:
            # 执行图
            final_state = await self.compiled_graph.ainvoke(initial_state)

            # 计算生成时间
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()

            # 提取结果
            solution = final_state.get("solution", {})
            streaming_output = final_state.get("streaming_output", [])

            # 添加生成时间
            if solution:
                solution["generation_time"] = generation_time
                solution["created_at"] = datetime.now().isoformat()

            print(f"\n{'='*70}")
            print(f"方案生成完成！耗时: {generation_time:.2f}秒")
            print(f"{'='*70}\n")

            return {
                "success": True,
                "solution": solution,
                "streaming_output": streaming_output,
                "generation_time": generation_time
            }

        except Exception as e:
            print(f"\n[ERROR] Solution generation failed: {e}")
            import traceback
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "streaming_output": initial_state.get("streaming_output", [])
            }

    def generate_solution(
        self,
        input_data: dict[str, Any],
        on_stream_chunk: Optional[callable] = None
    ) -> dict[str, Any]:
        """
        同步生成数据中心建设方案

        Args:
            input_data: 用户输入的需求数据
            on_stream_chunk: 流式输出回调函数

        Returns:
            包含方案和流式输出的字典
        """
        start_time = datetime.now()

        print("\n" + "="*70)
        print("开始生成数据中心建设方案")
        print("="*70)

        # 初始化状态
        initial_state: GraphState = {
            "requirement": input_data,
            "user_id": "user_" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "current_step": "start",
            "next_step": "",
            "debate_round": 1,
            "max_debate_rounds": 5,
            "consensus_reached": False,
            "should_continue_debate": True,
            "economic_opinion": None,
            "power_reliability_opinion": None,
            "environmental_opinion": None,
            "debate_history": [],
            "consensus_score": 0.0,
            "solution": {},
            "streaming_output": []
        }

        try:
            # 执行图
            final_state = self.compiled_graph.invoke(initial_state)

            # 计算生成时间
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()

            # 提取结果
            solution = final_state.get("solution", {})
            streaming_output = final_state.get("streaming_output", [])

            # 添加生成时间
            if solution:
                solution["generation_time"] = generation_time
                solution["created_at"] = datetime.now().isoformat()

            print(f"\n{'='*70}")
            print(f"方案生成完成！耗时: {generation_time:.2f}秒")
            print(f"{'='*70}\n")

            return {
                "success": True,
                "solution": solution,
                "streaming_output": streaming_output,
                "generation_time": generation_time
            }

        except Exception as e:
            print(f"\n[ERROR] Solution generation failed: {e}")
            import traceback
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "streaming_output": initial_state.get("streaming_output", [])
            }

    def get_system_status(self) -> dict[str, Any]:
        """获取系统状态"""
        return {
            "coordinator": {
                "status": "ready",
                "version": "2.0",
                "architecture": "LangChain + LangGraph",
                "last_activity": datetime.now().isoformat()
            },
            "graph": {
                "nodes": list(self.graph.nodes.keys()),
                "edges_count": len(self.graph.edges)
            },
            "memory": {
                "type": "ExpertSharedMemory",
                "history_length": len(self.memory.chat_history),
                "has_summary": bool(self.memory.summary)
            }
        }

    def clear_memory(self):
        """清空记忆"""
        self.memory.clear()
        print("记忆已清空")

    def explain_solution(
        self,
        solution: dict[str, Any],
        detail_level: str = "summary"
    ) -> str:
        """
        解释建设方案

        Args:
            solution: 建设方案
            detail_level: 详细程度 (summary/detail/full)

        Returns:
            解释文本
        """
        if detail_level == "summary":
            return self._generate_summary_explanation(solution)
        elif detail_level == "detail":
            return self._generate_detailed_explanation(solution)
        else:
            return self._generate_full_explanation(solution)

    def _generate_summary_explanation(self, solution: dict) -> str:
        """生成摘要解释"""
        return f"""
# 数据中心建设方案摘要

## 基本信息
- 方案名称: {solution.get('name', '未命名')}
- 版本: {solution.get('version', '1.0')}
- 总体评分: {solution.get('overall_scores', {}).get('overall', 0):.2f}
- 置信度: {solution.get('confidence', 0.8):.2f}

## 方案概述
{solution.get('summary', '无概述')}

## 关键指标
- 总成本: {solution.get('key_metrics', {}).get('total_cost', 0):.1f}万元
- PUE: {solution.get('key_metrics', {}).get('pue', 0)}
- 绿电比例: {solution.get('key_metrics', {}).get('green_power_ratio', 0)*100:.0f}%
- Tier级别: {solution.get('key_metrics', {}).get('tier_level', 0)}
- 预期可用性: {solution.get('key_metrics', {}).get('expected_availability', 0):.1f}%
- 年碳排放: {solution.get('key_metrics', {}).get('annual_carbon_emission', 0):.1f}吨
"""

    def _generate_detailed_explanation(self, solution: dict) -> str:
        """生成详细解释"""
        explanation = self._generate_summary_explanation(solution)

        explanation += "\n## 各维度分析\n"

        # 经济性
        economic = solution.get("economic_section", {})
        if economic:
            explanation += f"\n### 经济性\n"
            explanation += f"{economic.get('description', '')}\n"
            explanation += f"建议: {', '.join(economic.get('recommendations', []))}\n"

        # 供电可靠性
        power = solution.get("power_reliability_section", {})
        if power:
            explanation += f"\n### 供电可靠性\n"
            explanation += f"{power.get('description', '')}\n"
            explanation += f"建议: {', '.join(power.get('recommendations', []))}\n"

        # 环保性
        environmental = solution.get("environmental_section", {})
        if environmental:
            explanation += f"\n### 环保性\n"
            explanation += f"{environmental.get('description', '')}\n"
            explanation += f"建议: {', '.join(environmental.get('recommendations', []))}\n"

        return explanation

    def _generate_full_explanation(self, solution: dict) -> str:
        """生成完整解释"""
        explanation = self._generate_detailed_explanation(solution)

        # 权衡说明
        trade_offs = solution.get("trade_offs", [])
        if trade_offs:
            explanation += "\n## 权衡说明\n"
            for trade_off in trade_offs:
                explanation += f"- {trade_off.get('conflict', '')}: {trade_off.get('resolution', '')}\n"

        # 风险评估
        risks = solution.get("risks", [])
        if risks:
            explanation += "\n## 风险评估\n"
            for risk in risks:
                explanation += f"- [{risk.get('type', '').upper()}] {risk.get('description', '')}\n"

        # 最终建议
        recommendations = solution.get("recommendations", [])
        if recommendations:
            explanation += "\n## 最终建议\n"
            for i, rec in enumerate(recommendations, 1):
                explanation += f"{i}. {rec}\n"

        return explanation


# 向后兼容的别名
AISystemCoordinatorV2 = AISystemCoordinator
