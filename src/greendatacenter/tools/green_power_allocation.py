"""
绿电分配优化工具 (Green Power Allocation Tool)

功能:
    - 根据目标城市生成光伏/风电出力曲线
    - 基于差分进化算法优化风电/光伏/储能装机容量配比
    - 在满足绿电消纳率约束下最小化总投资成本

使用 @tool 装饰器注册，供智能体通过 tool-calling 调用。
"""

from pathlib import Path
import sys
from typing import Any, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from greendatacenter.tools.DE import (
    CSV_DIR,
    DEFAULT_LOAD_CSV_PATH,
    OUTPUT_DIR,
    run_capacity_optimization,
)
from greendatacenter.tools.pv_sim import generate_pv_profile
from greendatacenter.tools.wind_sim import generate_wind_profile


class GreenPowerAllocationInput(BaseModel):
    """绿电分配优化工具的输入 Schema"""

    location: str = Field(
        ..., description="数据中心所在地点，如 '北京'、'贵阳'"
    )
    green_power_ratio: float = Field(
        ..., description="绿电消纳率目标（0-1）"
    )
    load_mw: float = Field(
        ..., gt=0, description="数据中心总负荷（MW）"
    )
    sim_hours: int = Field(
        ..., gt=0, le=8760, description="仿真时长（小时）"
    )
    year: Optional[int] = Field(
        default=2025, description="气象数据年份，用于 8760h 仿真"
    )
    date: Optional[str] = Field(
        default=None, description="仿真日期（YYYY-MM-DD），仅 sim_hours<=24 时生效"
    )
    load_csv_path: Optional[str] = Field(
        default=None,
        description="自定义负荷系数 CSV 路径。若省略则使用默认 Load.csv",
    )
    pv_tilt: Optional[float] = Field(
        default=None, description="光伏倾角（度），省略则取当地纬度"
    )
    pv_azimuth: float = Field(
        default=180.0, description="光伏方位角（度），180 为正南"
    )
    wind_cut_in_ms: float = Field(
        default=3.0, gt=0, description="风机切入风速（m/s）"
    )
    wind_rated_ms: float = Field(
        default=12.0, gt=0, description="风机额定风速（m/s）"
    )
    wind_cut_out_ms: float = Field(
        default=25.0, gt=0, description="风机切出风速（m/s）"
    )
    maxiter: int = Field(
        default=60, gt=0, description="差分进化最大迭代次数"
    )
    popsize: int = Field(
        default=10, gt=0, description="差分进化种群大小"
    )
    seed: int = Field(
        default=42, description="随机种子"
    )
    wind_capacity_bounds: Optional[list[float]] = Field(
        default=None, description="风电装机容量范围（MW），如 [1, 500]"
    )
    pv_capacity_bounds: Optional[list[float]] = Field(
        default=None, description="光伏装机容量范围（MW），如 [1, 500]"
    )
    storage_capacity_bounds: Optional[list[float]] = Field(
        default=None, description="储能容量范围（MWh），如 [20, 500]"
    )
    week_start_hour: int = Field(
        default=0, ge=0, description="平衡图展示的起始小时"
    )
    disp: bool = Field(
        default=False, description="是否输出优化迭代过程"
    )


def _safe_file_stem(text: str) -> str:
    return "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in text).strip("_") or "location"


def _recommended_storage_min_mwh(load_mw: float, green_power_ratio: float, sim_hours: int) -> float:
    """
    Provide a modest default storage floor for realistic data-center demos.

    Rationale:
    - Pure cost minimization tends to collapse storage to ~0 whenever the
      direct green target can be met by oversizing wind/PV alone.
    - Real projects usually keep a small storage base for smoothing,
      dispatch flexibility, and operational resilience.
    """
    load_mw = max(float(load_mw), 0.0)
    green_power_ratio = max(0.0, min(1.0, float(green_power_ratio)))

    if green_power_ratio >= 0.6:
        duration_hours = 0.20
    elif green_power_ratio >= 0.3:
        duration_hours = 0.12
    else:
        duration_hours = 0.08

    if sim_hours >= 8760:
        duration_hours += 0.05

    recommended = load_mw * duration_hours
    return round(max(3.0, recommended), 2)


@tool("green_power_allocation", args_schema=GreenPowerAllocationInput, return_direct=True)
def green_power_allocation_tool(
    location: str,
    green_power_ratio: float,
    load_mw: float,
    sim_hours: int,
    year: Optional[int] = 2025,
    date: Optional[str] = None,
    load_csv_path: Optional[str] = None,
    pv_tilt: Optional[float] = None,
    pv_azimuth: float = 180.0,
    wind_cut_in_ms: float = 3.0,
    wind_rated_ms: float = 12.0,
    wind_cut_out_ms: float = 25.0,
    maxiter: int = 60,
    popsize: int = 10,
    seed: int = 42,
    wind_capacity_bounds: Optional[list[float]] = None,
    pv_capacity_bounds: Optional[list[float]] = None,
    storage_capacity_bounds: Optional[list[float]] = None,
    week_start_hour: int = 0,
    disp: bool = False,
) -> dict[str, Any]:
    """
    根据数据中心所在城市生成光伏和风电出力曲线，基于差分进化算法优化风电/光伏/储能
    的装机容量配比。在满足用户指定的绿电消纳率目标约束下，最小化总投资成本。
    输入包括：地点、绿电消纳率目标(0-1)、总负荷(MW)、仿真时长等。

    调参说明：
        - wind_capacity_bounds / pv_capacity_bounds / storage_capacity_bounds: 限制装机搜索范围
        - maxiter / popsize / seed: 优化器收敛速度与稳定性
        - week_start_hour: 平衡图展示窗口
        - green_power_ratio: 目标越高，装机规模通常更大
    """
    simulation_mode = "24h" if sim_hours <= 24 else "8760h"
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pv_csv_path = CSV_DIR / "PV.csv"
    wind_csv_path = CSV_DIR / "Wind.csv"

    sys.stdout.write("[green_power_allocation] Generating PV profile...\n")
    sys.stdout.flush()
    pv_result = generate_pv_profile(
        city=location,
        date=date,
        mode=simulation_mode,
        year=year,
        tilt=pv_tilt,
        azimuth=pv_azimuth,
        csv_output_path=pv_csv_path,
    )
    sys.stdout.write("[green_power_allocation] Generating wind profile...\n")
    sys.stdout.flush()
    wind_result = generate_wind_profile(
        city=location,
        date=date,
        mode=simulation_mode,
        year=year,
        cut_in_ms=wind_cut_in_ms,
        rated_ms=wind_rated_ms,
        cut_out_ms=wind_cut_out_ms,
        csv_output_path=wind_csv_path,
    )

    safe_location = _safe_file_stem(location)
    plot_output_path = OUTPUT_DIR / f"green_power_balance_{safe_location}_{sim_hours}h.png"
    resolved_load_csv_path = Path(load_csv_path) if load_csv_path else (
        DEFAULT_LOAD_CSV_PATH if DEFAULT_LOAD_CSV_PATH.exists() else None
    )

    if storage_capacity_bounds:
        resolved_storage_bounds = tuple(storage_capacity_bounds)
    else:
        storage_floor = _recommended_storage_min_mwh(
            load_mw=load_mw,
            green_power_ratio=green_power_ratio,
            sim_hours=sim_hours,
        )
        resolved_storage_bounds = (storage_floor, 500)

    resolved_bounds = (
        tuple(wind_capacity_bounds) if wind_capacity_bounds else (1, 500),
        tuple(pv_capacity_bounds) if pv_capacity_bounds else (1, 500),
        resolved_storage_bounds,
    )

    sys.stdout.write("[green_power_allocation] Running DE optimization...\n")
    sys.stdout.flush()
    optimization_result = run_capacity_optimization(
        data_center_load_mw=load_mw,
        target_green_ratio=green_power_ratio,
        sim_hours=sim_hours,
        load_csv_path=resolved_load_csv_path,
        wind_csv_path=wind_csv_path,
        pv_csv_path=pv_csv_path,
        bounds=resolved_bounds,
        plot_output_path=plot_output_path,
        week_start_hour=week_start_hour,
        maxiter=maxiter,
        popsize=popsize,
        seed=seed,
        disp=disp,
    )

    return {
        "status": "success",
        "inputs": {
            "location": location,
            "green_power_ratio": green_power_ratio,
            "load_mw": load_mw,
            "sim_hours": sim_hours,
            "year": year,
            "date": date,
            "bounds": {
                "wind_capacity_bounds": resolved_bounds[0],
                "pv_capacity_bounds": resolved_bounds[1],
                "storage_capacity_bounds": resolved_bounds[2],
            },
            "week_start_hour": week_start_hour,
            "maxiter": maxiter,
            "popsize": popsize,
            "seed": seed,
        },
        "generated_files": {
            "pv_csv": str(pv_csv_path),
            "wind_csv": str(wind_csv_path),
            "load_csv": str(resolved_load_csv_path) if resolved_load_csv_path is not None else None,
            "balance_plot": str(plot_output_path),
        },
        "pv_profile": {
            "mode": pv_result["mode"],
            "time_range": pv_result["time_range"],
            "summary": pv_result["summary"],
        },
        "wind_profile": {
            "mode": wind_result["mode"],
            "time_range": wind_result["time_range"],
            "summary": wind_result["summary"],
        },
        "optimization": optimization_result,
    }


if __name__ == "__main__":
    result = green_power_allocation_tool.invoke({
        "location": "北京",
        "green_power_ratio": 0.3,
        "load_mw": 40.0,
        "sim_hours": 8760,
        "year": 2025,
        "pv_azimuth": 180.0,
        "wind_cut_in_ms": 3.0,
        "wind_rated_ms": 12.0,
        "wind_cut_out_ms": 25.0,
        "maxiter": 60,
        "popsize": 10,
        "seed": 42,
        "wind_capacity_bounds": [1, 500],
        "pv_capacity_bounds": [1, 500],
        "storage_capacity_bounds": [20, 500],
        "week_start_hour": 0,
        "disp": False,
    })

    print("=== 绿电分配优化结果 ===")
    print(f"方案地点: {result['inputs']['location']}")
    print(f"目标绿电占比: {result['inputs']['green_power_ratio']}")
    print(f"总负荷(MW): {result['inputs']['load_mw']}")
    print("\n--- 优化容量 ---")
    opt = result["optimization"]
    print(f"风电装机(MW): {opt['wind_capacity_mw']:.2f}")
    print(f"光伏装机(MW): {opt['pv_capacity_mw']:.2f}")
    print(f"储能容量(MWh): {opt['storage_capacity_mwh']:.2f}")
