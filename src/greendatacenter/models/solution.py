"""
建设方案数据模型
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SolutionStatus(str, Enum):
    """方案状态"""
    DRAFT = "draft"  # 草稿
    REVIEW = "review"  # 审核中
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝


class SolutionSection(BaseModel):
    """方案子部分"""

    id: str = Field(default="", description="部分ID")
    name: str = Field(..., description="部分名称")
    description: str = Field(..., description="描述")
    content: dict[str, Any] = Field(default_factory=dict, description="内容")
    metrics: dict[str, float] = Field(default_factory=dict, description="关键指标")
    justification: str = Field(default="", description="设计理由")

    def model_post_init(self, __context):
        """模型初始化后处理"""
        if not self.id:
            self.id = f"sec_{self.name.lower().replace(' ', '_')}"


class Solution(BaseModel):
    """数据中心建设方案"""

    id: str = Field(default="", description="方案ID")
    requirement_id: str = Field(..., description="关联的需求ID")
    status: SolutionStatus = Field(default=SolutionStatus.DRAFT, description="方案状态")

    # 方案基本信息
    name: str = Field(..., description="方案名称")
    summary: str = Field(default="", description="方案摘要")
    version: str = Field(default="1.0", description="版本号")

    # 方案各部分
    economic_section: Optional[SolutionSection] = Field(None, description="经济性方案")
    power_reliability_section: Optional[SolutionSection] = Field(None, description="供电可靠性方案")
    environmental_section: Optional[SolutionSection] = Field(None, description="环保性方案")

    # 方案总体评价
    overall_scores: dict[str, float] = Field(default_factory=dict, description="总体评分")
    trade_offs: list[dict] = Field(default_factory=list, description="权衡点说明")

    # 关键指标
    key_metrics: dict[str, Any] = Field(default_factory=dict, description="关键指标")

    # 设备清单
    equipment_list: list[dict] = Field(default_factory=list, description="设备清单")

    # 成本估算
    cost_breakdown: dict[str, float] = Field(default_factory=dict, description="成本分解")

    # 风险评估
    risks: list[dict] = Field(default_factory=list, description="风险清单")

    # 建议
    recommendations: list[str] = Field(default_factory=list, description="改进建议")

    # 元数据
    generated_by: str = Field(default="ai_system", description="生成者")
    confidence: float = Field(default=0.8, ge=0, le=1, description="置信度")
    generation_time: float = Field(default=0.0, description="生成耗时(秒)")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "华东某数据中心一期建设方案V1.0",
                "summary": "基于100个机柜、500kW电力需求的高可靠性绿色数据中心建设方案",
                "overall_scores": {"economic": 0.85, "reliability": 0.9, "environmental": 0.88},
                "key_metrics": {
                    "total_cost": 1800,
                    "pue": 1.28,
                    "green_power_ratio": 0.75,
                    "tier_level": 3
                },
                "cost_breakdown": {
                    "equipment": 1080,
                    "construction": 360,
                    "design": 180,
                    "contingency": 180
                },
                "recommendations": [
                    "建议增加市电双路接入以提高可靠性",
                    "建议优先采购一级能效设备以降低能耗"
                ]
            }
        }

    def model_post_init(self, __context):
        """模型初始化后处理"""
        if not self.id:
            self.id = f"sol_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def calculate_overall_score(self) -> float:
        """计算总体评分"""
        if not self.overall_scores:
            return 0.0

        # 使用优先级加权计算
        weights = {
            "economic": 0.3,
            "reliability": 0.4,
            "environmental": 0.3
        }

        total_score = 0.0
        total_weight = 0.0

        for key, weight in weights.items():
            if key in self.overall_scores:
                total_score += self.overall_scores[key] * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def add_section(self, section: SolutionSection):
        """添加方案部分"""
        if section.name == "经济性":
            self.economic_section = section
        elif section.name == "供电可靠性":
            self.power_reliability_section = section
        elif section.name == "环保性":
            self.environmental_section = section
