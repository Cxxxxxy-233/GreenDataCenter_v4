"""
图状态定义
"""

from typing import Any, Literal, Optional, TypedDict

from pydantic import Field
from pydantic import BaseModel as PydanticBaseModel


class UserRequirement(PydanticBaseModel):
    """用户需求参数 — 前端输入"""

    # ===== 基本信息 =====
    location: str = Field(..., description="数据中心所在地点，如 '北京'、'贵阳'")
    planned_load_kw: float = Field(..., gt=0, description="数据中心总负荷（kW）")
    green_power_ratio: float = Field(..., ge=0, le=1, description="绿电消纳率目标（0-1）")
    planned_area: float = Field(..., gt=0, description="数据中心计划建筑面积（m²）")
    budget_constraint: float = Field(..., gt=0, description="预算约束（万元）")

    # ===== 制冷 =====
    cooling_technology: str = Field(
        default="浸没式液冷",
        description="制冷技术，如 '浸没式液冷'、'蒸发冷却'、'风冷'"
    )

    # ===== 供电与可靠性 =====
    machine_room_grade: Literal["A+", "A", "B", "C"] = Field(
        default="A", description="机房等级（A+/A/B/C），对应 GB 50174-2017"
    )
    pue_target: float = Field(default=1.3, ge=1.0, le=3.0, description="PUE 目标值")

    # ===== 仿真与优化 =====
    sim_hours: int = Field(default=160, gt=0, le=8760, description="仿真时长（小时）")
    year: Optional[int] = Field(default=2025, description="气象数据年份")
    date: Optional[str] = Field(
        default=None, description="仿真日期（YYYY-MM-DD），仅 sim_hours<=24 时生效"
    )

    # ===== 光伏参数 =====
    pv_tilt: Optional[float] = Field(default=None, description="光伏倾角（度），None 则取当地纬度")
    pv_azimuth: float = Field(default=180.0, description="光伏方位角（度），180 为正南")

    # ===== 风电参数 =====
    wind_cut_in_ms: float = Field(default=3.0, gt=0, description="风机切入风速（m/s）")
    wind_rated_ms: float = Field(default=12.0, gt=0, description="风机额定风速（m/s）")
    wind_cut_out_ms: float = Field(default=25.0, gt=0, description="风机切出风速（m/s）")

    # ===== 经济与碳排放 =====
    computing_power_density: float = Field(
        default=8.0, gt=0, description="单机柜算力功率密度（kW/机柜）"
    )
    carbon_emission_factor: float = Field(
        default=0.5, ge=0, description="电网碳排放因子（kg CO2/kWh）"
    )
    electricity_prices: dict[str, float] = Field(
        default_factory=lambda: {
            "尖峰电价": 0.5,
            "高峰电价": 0.4,
            "平段电价": 0.3,
            "低谷电价": 0.25,
            "深谷电价": 0.2,
        },
        description="各时段电价（元/kWh），键为时段名称",
    )

    # ===== 优化器高级参数 =====
    maxiter: int = Field(default=60, gt=0, description="差分进化最大迭代次数")
    popsize: int = Field(default=10, gt=0, description="差分进化种群大小")
    seed: int = Field(default=42, description="随机种子")

    # ===== 计算属性 =====
    @property
    def planned_load_mw(self) -> float:
        """总负荷（MW）"""
        return self.planned_load_kw / 1000.0

    class Config:
        extra = "allow"


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
    user_requirement: UserRequirement  # 结构化用户需求参数
    requirement: dict[str, Any]  # 原始/归一化需求字典

    # ===== 流程控制 =====
    current_step: str  # 当前步骤
    next_step: str  # 下一步骤

    # ===== 辩论控制 =====
    debate_round: int  # 当前辩论轮次
    max_debate_rounds: int  # 最大辩论轮数
    consensus_reached: bool  # 是否达成共识
    should_continue_debate: bool  # 是否继续辩论

    # ===== 工具计算结果 =====
    power_supply_plan: dict[str, Any]  # 供电方案配置结果
    green_power_result: dict[str, Any]  # 绿电分配优化结果
    economic_analysis_result: dict[str, Any]  # 经济性分析结果
    cooling_result: dict[str, Any]  # 制冷方案计算结果

    # ===== 预算控制 =====
    budget_feedback: str  # 预算超限反馈
    budget_retry_count: int  # 预算超限重试次数
    max_budget_retries: int  # 预算超限最大重试次数

    # ===== 初稿生成专家反馈 =====
    draft_plan_feedback: str  # 辩论反馈给初稿生成专家
    draft_plan_summary: str  # 初稿摘要

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
NODE_DRAFT_PLAN_AGENT = "draft_plan_agent"
NODE_COST_CALCULATION = "cost_calculation"
NODE_ECONOMIC_ANALYSIS = "economic_analysis"
NODE_POWER_RELIABILITY_ANALYSIS = "power_reliability_analysis"
NODE_ENVIRONMENTAL_ANALYSIS = "environmental_analysis"
NODE_DEBATE_START = "debate_start"
NODE_DEBATE_ROUND = "debate_round"
NODE_DEBATE_END = "debate_end"
NODE_ARBITRATOR = "arbitrator"
NODE_FINAL_REPORT = "final_report"
NODE_OUTPUT = "output"

# 路由名称常量
ROUTE_CHECK_CONSENSUS = "check_consensus"
ROUTE_CHECK_MAX_ROUNDS = "check_max_rounds"
ROUTE_DEBATE_CONTINUE = "debate_continue"
ROUTE_DEBATE_STOP = "debate_stop"

# 条件名称
CONDITION_CONTINUE_DEBATE = "should_continue_debate"
CONDITION_MAX_ROUNDS_REACHED = "max_rounds_reached"
