"""
需求数据模型
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RequirementType(str, Enum):
    """需求类型"""
    NEW_CONSTRUCTION = "new_construction"  # 新建
    EXPANSION = "expansion"  # 扩建
    UPGRADE = "upgrade"  # 升级


class Requirement(BaseModel):
    """数据中心建设需求"""

    # 基础信息
    id: str = Field(default="", description="需求ID")
    name: str = Field(..., description="需求名称")
    description: str = Field(default="", description="需求描述")
    requirement_type: RequirementType = Field(
        default=RequirementType.NEW_CONSTRUCTION,
        description="需求类型"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    # 规模需求
    rack_count: Optional[int] = Field(None, ge=0, description="机柜数量")
    server_count: Optional[int] = Field(None, ge=0, description="服务器数量")
    floor_area: Optional[float] = Field(None, gt=0, description="场地面积 (m²)")
    ceiling_height: Optional[float] = Field(None, gt=0, description="层高 (m)")

    # 电力需求
    total_power: Optional[float] = Field(None, gt=0, description="总功率需求 (kW)")
    power_density: Optional[float] = Field(None, gt=0, description="功率密度 (kW/rack)")
    tier_level: Optional[int] = Field(None, ge=1, le=4, description="可靠性级别 (1-4)")

    # 制冷需求
    pue_target: Optional[float] = Field(None, gt=1.0, description="PUE目标值")
    cooling_method: Optional[str] = Field(None, description="制冷方式偏好")
    temperature_range: Optional[tuple[float, float]] = Field(None, description="温度范围 (°C)")

    # 网络需求
    bandwidth: Optional[float] = Field(None, gt=0, description="带宽需求 (Gbps)")
    network_redundancy: Optional[str] = Field(None, description="网络冗余要求")

    # 环保需求
    green_power_ratio: Optional[float] = Field(None, ge=0, le=1, description="绿电比例目标")
    carbon_emission_target: Optional[float] = Field(None, ge=0, description="碳排放目标 (tCO2e/年)")

    # 扩展需求
    budget: Optional[float] = Field(None, gt=0, description="预算上限 (万元)")
    build_period: Optional[int] = Field(None, gt=0, description="建设周期 (月)")
    additional_requirements: list[str] = Field(default_factory=list, description="附加需求")

    # 目标与约束
    objectives: list[str] = Field(default_factory=list, description="项目目标")
    constraints: list[str] = Field(default_factory=list, description="约束条件")
    priorities: dict[str, int] = Field(default_factory=dict, description="优先级 (经济性/可靠性/环保性)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "华东某数据中心一期建设",
                "description": "建设100个机柜的数据中心，要求高可靠性和绿色节能",
                "rack_count": 100,
                "total_power": 500,
                "power_density": 5,
                "tier_level": 3,
                "pue_target": 1.3,
                "green_power_ratio": 0.7,
                "budget": 2000,
                "objectives": ["降低PUE", "提高可靠性", "控制成本"],
                "priorities": {"economic": 3, "reliability": 5, "environmental": 4}
            }
        }

    def model_post_init(self, __context):
        """模型初始化后处理"""
        if not self.id:
            self.id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 设置默认优先级
        if not self.priorities:
            self.priorities = {
                "economic": 3,
                "reliability": 4,
                "environmental": 4
            }

    def validate_requirement(self) -> tuple[bool, list[str]]:
        """验证需求完整性"""
        errors = []

        # 检查必要参数
        if self.rack_count is None and self.server_count is None:
            errors.append("必须提供机柜数量或服务器数量")

        if self.total_power is None:
            errors.append("必须提供总功率需求")

        if self.tier_level is None:
            errors.append("必须提供可靠性级别")

        # 检查参数合理性
        if self.rack_count and self.total_power:
            calculated_density = self.total_power / self.rack_count
            if calculated_density > 20:
                errors.append(f"功率密度过高 ({calculated_density:.1f} kW/rack)，超过20 kW/rack")

        if self.pue_target and self.pue_target < 1.05:
            errors.append("PUE目标值过低，实际工程中难以达到")

        if self.green_power_ratio and self.green_power_ratio > 1.0:
            errors.append("绿电比例不能超过100%")

        return len(errors) == 0, errors
