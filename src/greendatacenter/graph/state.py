"""
图状态定义
"""

from typing import Any, Literal, TypedDict

from pydantic import Field
from pydantic import BaseModel as PydanticBaseModel


class ExpertOpinion(PydanticBaseModel):
    """专家意见"""
    expert_type: str = Field(..., description="专家类型")
    expert_name: str = Field(..., description="专家名称")
    summary: str = Field(..., description="意见摘要")
    reasoning: str = Field(..., description="推理过程")
    scores: dict[str, float] = Field(default_factory=dict, description="评分")
    metrics: dict[str, Any] = Field(default_factory=dict, description="量化指标")
    recommendations: list[str] = Field(default_factory=list, description="建议")
    concerns: list[str] = Field(default_factory=list, description="关注点")
    confidence: float = Field(default=0.8, ge=0, le=1, description="置信度")


class DebateMessage(PydanticBaseModel):
    """辩论消息"""
    round: int = Field(..., description="轮次")
    speaker: str = Field(..., description="发言者")
    listener: str = Field(default="", description="倾听者")
    message_type: str = Field(..., description="消息类型")
    content: str = Field(..., description="消息内容")


class GraphState(TypedDict):
    """图状态"""

    # ===== 输入 =====
    requirement: dict[str, Any]  # 原始需求
    user_id: str  # 用户ID

    # ===== 流程控制 =====
    current_step: str  # 当前步骤
    next_step: str  # 下一步骤

    # ===== 辩论控制 =====
    debate_round: int  # 当前辩论轮次
    max_debate_rounds: int  # 最大辩论轮数
    consensus_reached: bool  # 是否达成共识
    should_continue_debate: bool  # 是否继续辩论

    # ===== 专家意见 =====
    economic_opinion: ExpertOpinion  # 经济性专家意见
    power_reliability_opinion: ExpertOpinion  # 供电可靠性专家意见
    environmental_opinion: ExpertOpinion  # 环保性专家意见

    # ===== 辩论历史 =====
    debate_history: list[DebateMessage]  # 辩论历史

    # ===== 评估 =====
    consensus_score: float  # 共识度分数

    # ===== 输出 =====
    solution: dict[str, Any]  # 最终方案

    # ===== 流式输出 =====
    streaming_output: list[dict[str, Any]]  # 流式输出记录


# 节点名称常量
NODE_REQUIREMENT_PARSER = "requirement_parser"
NODE_ECONOMIC_ANALYSIS = "economic_analysis"
NODE_POWER_RELIABILITY_ANALYSIS = "power_reliability_analysis"
NODE_ENVIRONMENTAL_ANALYSIS = "environmental_analysis"
NODE_DEBATE_START = "debate_start"
NODE_DEBATE_ROUND = "debate_round"
NODE_DEBATE_END = "debate_end"
NODE_ARBITRATOR = "arbitrator"
NODE_OUTPUT = "output"

# 路由名称常量
ROUTE_CHECK_CONSENSUS = "check_consensus"
ROUTE_CHECK_MAX_ROUNDS = "check_max_rounds"
ROUTE_DEBATE_CONTINUE = "debate_continue"
ROUTE_DEBATE_STOP = "debate_stop"

# 条件名称
CONDITION_CONTINUE_DEBATE = "should_continue_debate"
CONDITION_MAX_ROUNDS_REACHED = "max_rounds_reached"
