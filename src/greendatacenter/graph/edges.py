"""
边和条件函数
"""

from typing import Literal


def should_continue_debate(state: dict) -> str:
    """
    判断是否继续辩论

    Args:
        state: 图状态

    Returns:
        "continue" 或 "stop"
    """
    # 检查共识是否达成
    if state.get("consensus_reached", False):
        print("\n[OK] 已达成共识，停止辩论")
        return "stop"

    # 检查是否超过最大轮数
    debate_round = state.get("debate_round", 0)
    max_rounds = state.get("max_debate_rounds", 5)

    if debate_round >= max_rounds:
        print(f"\n[OK] 已达到最大辩论轮数({max_rounds})，强制停止辩论")
        return "stop"

    # 检查是否应该继续
    if not state.get("should_continue_debate", True):
        print("\n[OK] 辩论条件不满足，停止辩论")
        return "stop"

    return "continue"


def check_debate_status(state: dict) -> Literal["revise", "end"]:
    """
    检查辩论状态

    Args:
        state: 图状态

    Returns:
        "continue" 或 "end"
    """
    if should_continue_debate(state) == "continue":
        return "revise"
    return "end"


def check_budget_status(state: dict) -> Literal["retry", "continue"]:
    """
    检查预算状态

    Args:
        state: 图状态

    Returns:
        "retry" 或 "continue"
    """
    analysis = state.get("economic_analysis_result", {})
    is_over_budget = analysis.get("is_over_budget", False)
    retry_count = int(state.get("budget_retry_count", 0) or 0)
    max_retries = int(state.get("max_budget_retries", 2) or 2)

    if is_over_budget and retry_count <= max_retries:
        print(f"\n[WARN] 超出预算，触发重试 ({retry_count}/{max_retries})")
        return "retry"

    return "continue"
