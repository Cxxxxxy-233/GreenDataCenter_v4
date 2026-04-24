"""
专家意见数据模型
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ExpertType(str, Enum):
    """专家类型"""
    ECONOMIC = "economic"  # 经济性分析专家
    POWER_RELIABILITY = "power_reliability"  # 供电可靠性专家
    ENVIRONMENTAL = "environmental"  # 环保性分析专家


class OpinionType(str, Enum):
    """意见类型"""
    PRO = "pro"  # 支持
    CON = "con"  # 反对
    NEUTRAL = "neutral"  # 中立
    SUGGESTION = "suggestion"  # 建议


class ExpertOpinion(BaseModel):
    """专家意见"""

    id: str = Field(default="", description="意见ID")
    expert_type: ExpertType = Field(..., description="专家类型")
    expert_name: str = Field(..., description="专家名称")
    requirement_id: str = Field(..., description="关联的需求ID")

    # 意见内容
    opinion_type: OpinionType = Field(default=OpinionType.NEUTRAL, description="意见类型")
    summary: str = Field(..., description="意见摘要")
    reasoning: str = Field(..., description="推理过程")
    evidence: list[str] = Field(default_factory=list, description="支撑证据")

    # 评估指标
    scores: dict[str, float] = Field(default_factory=dict, description="各项指标评分")
    metrics: dict[str, Any] = Field(default_factory=dict, description="量化指标")

    # 建议
    recommendations: list[str] = Field(default_factory=list, description="改进建议")
    concerns: list[str] = Field(default_factory=list, description="关注点")

    # 元数据
    confidence: float = Field(default=0.8, ge=0, le=1, description="置信度")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    class Config:
        json_schema_extra = {
            "example": {
                "expert_type": "economic",
                "expert_name": "经济性分析专家-张工",
                "opinion_type": "pro",
                "summary": "方案在经济性方面较为合理",
                "reasoning": "设备选型考虑了成本效益，建设周期可控",
                "scores": {"cost_efficiency": 0.85, "roi": 0.78},
                "metrics": {"total_cost": 1800, "payback_period": 5},
                "recommendations": ["建议增加备用电源冗余以降低风险"],
                "concerns": ["部分设备价格波动风险"],
                "confidence": 0.85
            }
        }

    def model_post_init(self, __context):
        """模型初始化后处理"""
        if not self.id:
            self.id = f"op_{self.expert_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
