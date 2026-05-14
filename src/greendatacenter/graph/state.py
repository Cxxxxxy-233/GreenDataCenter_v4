"""
State models shared across the workflow graph.
"""

from typing import Any, Literal, Optional, TypedDict

from pydantic import Field
from pydantic import BaseModel as PydanticBaseModel


class UserRequirement(PydanticBaseModel):
    """Normalized user input for the planning workflow."""

    location: str = Field(..., description="Project location / city")
    planned_load_kw: float = Field(..., gt=0, description="Planned IT load in kW")
    green_power_ratio: float = Field(..., ge=0, le=1, description="Target total green power ratio, 0-1")
    planned_area: float = Field(..., gt=0, description="Planned gross floor area in square meters")
    direct_connection_ratio: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Target green direct-connection ratio, optional, 0-1",
    )
    budget_constraint: float = Field(..., gt=0, description="Budget constraint in lakh yuan")

    cooling_technology: str = Field(default="液冷", description="Preferred cooling technology")
    machine_room_grade: Literal["A+", "A", "B", "C"] = Field(
        default="A",
        description="Machine room grade aligned with GB 50174-2017",
    )
    pue_target: float = Field(default=1.3, ge=1.0, le=3.0, description="Target PUE")

    sim_hours: int = Field(default=160, gt=0, le=8760, description="Simulation horizon in hours")
    year: Optional[int] = Field(default=2025, description="Weather / resource data year")
    date: Optional[str] = Field(default=None, description="Simulation date in YYYY-MM-DD when using short simulation")

    pv_tilt: Optional[float] = Field(default=None, description="PV tilt angle in degrees")
    pv_azimuth: float = Field(default=180.0, description="PV azimuth angle in degrees")

    wind_cut_in_ms: float = Field(default=3.0, gt=0, description="Wind turbine cut-in speed in m/s")
    wind_rated_ms: float = Field(default=12.0, gt=0, description="Wind turbine rated speed in m/s")
    wind_cut_out_ms: float = Field(default=25.0, gt=0, description="Wind turbine cut-out speed in m/s")

    computing_power_density: float = Field(default=8.0, gt=0, description="Computing power density in kW per rack")
    carbon_emission_factor: float = Field(default=0.5, ge=0, description="Grid carbon emission factor in tCO2/MWh")
    electricity_prices: dict[str, float] = Field(
        default_factory=lambda: {
            "尖峰电价": 0.50,
            "高峰电价": 0.40,
            "平段电价": 0.30,
            "低谷电价": 0.25,
            "深谷电价": 0.20,
        },
        description="Time-of-use electricity prices in yuan/kWh",
    )

    maxiter: int = Field(default=60, gt=0, description="Differential evolution max iterations")
    popsize: int = Field(default=10, gt=0, description="Differential evolution population size")
    seed: int = Field(default=42, description="Random seed")

    @property
    def planned_load_mw(self) -> float:
        return self.planned_load_kw / 1000.0

    class Config:
        extra = "allow"


class ExpertOpinion(PydanticBaseModel):
    """Expert opinion payload used by the debate and arbitrator."""

    expert_type: str = Field(..., description="Expert type")
    expert_name: str = Field(..., description="Expert name")
    summary: str = Field(..., description="Summary")
    reasoning: str = Field(..., description="Reasoning")
    scores: dict[str, float] = Field(default_factory=dict, description="Normalized scores")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Quantitative metrics")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")
    concerns: list[str] = Field(default_factory=list, description="Concerns")
    confidence: float = Field(default=0.8, ge=0, le=1, description="Confidence")


class DebateMessage(PydanticBaseModel):
    """One debate message exchanged during the multi-expert discussion."""

    round: int = Field(..., description="Debate round number")
    speaker: str = Field(..., description="Speaker")
    listener: str = Field(default="", description="Listener")
    message_type: str = Field(..., description="Message type")
    content: str = Field(..., description="Message content")


class GraphState(TypedDict, total=False):
    """Workflow state exchanged between graph nodes."""

    user_requirement: UserRequirement
    requirement: dict[str, Any]

    current_step: str
    next_step: str

    debate_round: int
    max_debate_rounds: int
    consensus_reached: bool
    should_continue_debate: bool

    power_supply_plan: dict[str, Any]
    green_power_result: dict[str, Any]
    economic_analysis_result: dict[str, Any]
    cooling_result: dict[str, Any]

    budget_feedback: str
    budget_retry_count: int
    max_budget_retries: int
    draft_plan_feedback: str
    draft_plan_summary: str

    economic_opinion: ExpertOpinion
    power_reliability_opinion: ExpertOpinion
    environmental_opinion: ExpertOpinion

    debate_history: list[DebateMessage]
    consensus_score: float

    solution: dict[str, Any]
    streaming_output: list[dict[str, Any]]


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

ROUTE_CHECK_CONSENSUS = "check_consensus"
ROUTE_CHECK_MAX_ROUNDS = "check_max_rounds"
ROUTE_DEBATE_CONTINUE = "debate_continue"
ROUTE_DEBATE_STOP = "debate_stop"

CONDITION_CONTINUE_DEBATE = "should_continue_debate"
CONDITION_MAX_ROUNDS_REACHED = "max_rounds_reached"
