"""
供电方案配置工具 (Power Supply Configuration Tool)

功能:
    - 基于 GB 50174—2017 / YD/T 5235—2019 标准
    - 根据机房等级、总负荷、PUE目标等参数自动匹配最优供电方案
    - 输出供电方案描述、详细理由及结构化配置JSON

使用 @tool 装饰器注册，供智能体通过 tool-calling 调用。
"""

from typing import Any, Dict, Literal, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field


POWER_SUPPLY_SCHEMES = {
    "A+": {
        "external_source": "三路电源：双重工作电源 + 1路100%热备用电源",
        "transformer_redundancy": "主变N+2，配变M(1+2)",
        "bus_config": "380/220V 母线采用环形接线",
        "diesel_config": "取消柴发主备，仅保留保安负荷用柴发",
        "reason": "满足最高可靠性容错要求，利用电网热备用替代柴发以节省约79%投资并减少污染。",
        "cost_per_mw": 300  # 单位：万元/MW
    },
    "A": {
        "external_source": "两路电源：双重工作电源（每路100%负荷）",
        "transformer_redundancy": "主变N+1，配变2N（互为备用）",
        "bus_config": "380/220V 单母线分段接线",
        "diesel_config": "仅用于保安负荷",
        "reason": "符合A级容错标准，确保单一组件故障时不影响业务。",
        "cost_per_mw": 250  # 单位：万元/MW
    },
    "B": {
        "external_source": "两路电源：双重工作电源（每路100%负荷）",
        "transformer_redundancy": "主变N，配变N+1",
        "bus_config": "380/220V 单母线分段接线",
        "diesel_config": "宜配置柴油发电机组作为主电源备用",
        "reason": "经济平衡型配置，通过N+1冗余降低设备初投资。",
        "cost_per_mw": 180  # 单位：万元/MW
    },
    "C": {
        "external_source": "一路电源（如负荷>100MW宜双回路）",
        "transformer_redundancy": "主变N，配变N",
        "bus_config": "380/220V 单母线接线",
        "diesel_config": "应配置柴油发电机组作为主电源备用",
        "reason": "基础型配置，依赖柴发系统保障电力连续性。",
        "cost_per_mw": 120  # 单位：万元/MW
    }
}

VOLTAGE_LEVEL_CRITERIA = [
    {"threshold": 100, "voltage": "220 kV", "reason": "容量超过100MVA首选220kV，且电量电价最低，可显著降低运营成本。"},
    {"threshold": 40, "voltage": "110 kV", "reason": "匹配40~360MVA容量区间，采用单回或同塔双回线路供电。"},
    {"threshold": 30, "voltage": "66 kV", "reason": "匹配30~180MVA容量区间，兼顾投资与输送能力。"},
    {"threshold": 0, "voltage": "35 kV", "reason": "适用于30~60MVA中小型数据中心。"}
]


class PowerSupplyConfigInput(BaseModel):
    """供电方案配置工具的输入 Schema"""

    machine_room_grade: Literal["A+", "A", "B", "C"] = Field(
        ..., description="机房等级（A+/A/B/C），对应 GB 50174-2017"
    )
    total_load_mw: float = Field(
        ..., gt=0, description="数据中心总负荷（MW）"
    )
    pue_target: float = Field(
        ..., ge=1.0, le=3.0, description="PUE 目标值"
    )
    power_factor: float = Field(
        default=0.9, ge=0.8, le=1.0, description="功率因数（用于MW->MVA换算）"
    )
    external_voltage_override: Optional[str] = Field(
        default=None, description="外部电压等级指定，如 '110 kV'"
    )
    secondary_voltage_override: Optional[str] = Field(
        default=None, description="次级配电电压指定，如 '10 kV'"
    )


@tool("power_supply_config", args_schema=PowerSupplyConfigInput, return_direct=True)
def power_supply_config_tool(
    machine_room_grade: str,
    total_load_mw: float,
    pue_target: float,
    power_factor: float = 0.9,
    external_voltage_override: Optional[str] = None,
    secondary_voltage_override: Optional[str] = None,
) -> Dict[str, Any]:
    """
    基于 GB 50174—2017 / YD/T 5235—2019 标准，根据机房等级、总负荷、PUE目标
    自动匹配最优供电方案，返回供电方案描述、详细理由及结构化配置JSON。

    调参说明：
        - power_factor: 影响 MW->MVA 换算，进而影响外部电压档位选择
        - external_voltage_override: 强制指定外部电压等级
        - secondary_voltage_override: 强制指定次级配电电压
    """
    grade = machine_room_grade
    load_mw = total_load_mw
    pue = pue_target
    load_mva = load_mw / power_factor

    ext_voltage = None
    ext_reason = None
    if external_voltage_override:
        ext_voltage = external_voltage_override
        ext_reason = "外部电压等级由输入参数指定"
    else:
        for criteria in VOLTAGE_LEVEL_CRITERIA:
            if load_mva >= criteria["threshold"]:
                ext_voltage = criteria["voltage"]
                ext_reason = criteria["reason"]
                break

    selected_scheme = POWER_SUPPLY_SCHEMES.get(grade, POWER_SUPPLY_SCHEMES["A"])

    if secondary_voltage_override:
        secondary_dist = secondary_voltage_override
        secondary_reason = "次级配电电压由输入参数指定"
    else:
        secondary_dist = "10 kV"
        secondary_reason = "10kV在设备费与占地上均为最优，配变单台推荐2.5MVA以适配0.4kV断路器能力。"

    detailed_reasons = (
        f"【配置等级】: 选定 {grade} 级供电架构，{selected_scheme['reason']}\n"
        f"【外部供电】: 采用 {ext_voltage} 接入，理由：{ext_reason}\n"
        f"【次级配电】: 选定 {secondary_dist} 方案，原因：{secondary_reason}\n"
        f"【电气接线】: 主机房采用 {selected_scheme['bus_config']}，确保电力分配的可靠性。"
    )

    if grade == "A+":
        dist_transformers = "2.5 MVA / M(1+2)"
    elif grade == "A":
        dist_transformers = "2.5 MVA / 2N"
    elif grade == "B":
        dist_transformers = "2.5 MVA / N+1"
    else:
        dist_transformers = "2.5 MVA / N"

    return {
        "scheme_name": f"{grade}级-{ext_voltage} 供电一体化方案",
        "external_voltage": ext_voltage,
        "secondary_voltage": secondary_dist,
        "external_source_type": selected_scheme["external_source"],
        "redundancy_logic": selected_scheme["transformer_redundancy"],
        "bus_type": selected_scheme["bus_config"],
        "diesel_status": selected_scheme["diesel_config"],
        "reasons": detailed_reasons,
        "raw_json": {
            "machine_room_grade": grade,
            "total_load_mw": load_mw,
            "total_load_mva": round(load_mva, 2),
            "pue_target": pue,
            "power_factor": power_factor,
            "main_transformers": selected_scheme["transformer_redundancy"].split("，")[0],
            "distribution_transformers": dist_transformers,
            "cost_per_mw": selected_scheme["cost_per_mw"]
        }
    }


if __name__ == "__main__":
    result = power_supply_config_tool.invoke({
        "machine_room_grade": "A+",
        "total_load_mw": 120.0,
        "pue_target": 1.25,
    })

    print(f"\n推荐方案: {result['scheme_name']}")
    print("-" * 60)
    print(f"方案理由:\n{result['reasons']}")
    print("-" * 60)
    print("原始配置JSON:")
    import json
    print(json.dumps(result["raw_json"], indent=2, ensure_ascii=False))
