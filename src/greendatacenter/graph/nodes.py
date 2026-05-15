# -*- coding: utf-8 -*-
"""
鍥捐妭鐐瑰嚱鏁?- 淇鐗?"""

import io
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from pydantic import BaseModel as PydanticBaseModel

from greendatacenter.llm.config import create_economic_llm, create_power_reliability_llm, create_environmental_llm, create_arbitrator_llm, create_final_report_llm, get_llm
from greendatacenter.memory import ExpertSharedMemory
from greendatacenter.graph.state import GraphState, UserRequirement, ExpertOpinion, DebateMessage
from greendatacenter.tools.green_power_allocation import green_power_allocation_tool
from greendatacenter.tools.cooling import cooling_scheme_generator_tool
from greendatacenter.tools.power_supply_config import power_supply_config_tool

# Green power CAPEX factors: lakh yuan per MW / MWh.
COST_FACTORS = {
    "wind_per_mw": 420,
    "pv_per_mw": 350,
    "storage_per_mwh": 60,
}

# 寮哄埗UTF-8杈撳嚭锛堜粎鍦ㄤ氦浜掑紡鎺у埗鍙版ā寮忎笅锛?# 杩欎釜浼氬奖鍝嶇粓绔緭鍑轰笉瑕佽В寮€娉ㄩ噴
# if sys.platform == "win32" and sys.stdout.isatty():
#     import io
#     sys.stdout = io.TextIOWrapper(sys.stdout, encoding="utf-8")
#     sys.stderr = io.TextIOWrapper(sys.stderr, encoding="utf-8")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_score_value(value: Any, default: float = 0.5) -> float:
    numeric = _safe_float(value, default)
    if numeric > 1:
        if numeric <= 100:
            numeric = numeric / 100.0
        else:
            numeric = 1.0
    return max(0.0, min(1.0, numeric))


def _estimate_rack_count(requirement: dict[str, Any]) -> int:
    planned_load_kw = _safe_float(requirement.get("planned_load_kw"), 0.0)
    density = _safe_float(requirement.get("computing_power_density"), 8.0)
    if planned_load_kw <= 0 or density <= 0:
        return 0
    return max(1, round(planned_load_kw / density))


def _machine_grade_to_tier(machine_room_grade: str) -> int:
    mapping = {"A+": 4, "A": 3, "B": 2, "C": 1}
    return mapping.get((machine_room_grade or "").strip(), 3)


CITY_ENVIRONMENT_PRESETS: dict[str, dict[str, float]] = {
    "\u4e4c\u5170\u5bdf\u5e03": {"annual_temperature": 6.0},
    "\u5f20\u5bb6\u53e3": {"annual_temperature": 8.0},
    "\u5317\u4eac": {"annual_temperature": 13.0},
    "\u4e0a\u6d77": {"annual_temperature": 18.0},
    "\u676d\u5dde": {"annual_temperature": 17.5},
    "\u5e7f\u5dde": {"annual_temperature": 22.5},
    "\u6df1\u5733": {"annual_temperature": 23.0},
    "\u8d35\u9633": {"annual_temperature": 15.5},
    "\u4e3d\u6c5f": {"annual_temperature": 13.0},
    "\u6b66\u6c49": {"annual_temperature": 17.0},
    "\u897f\u5b89": {"annual_temperature": 14.0},
    "\u5357\u4eac": {"annual_temperature": 16.0},
    "\u4e09\u4e9a": {"annual_temperature": 25.0},
}


def _derive_environmental_data(requirement: dict[str, Any]) -> dict[str, Any]:
    location = str(requirement.get("location") or "").strip()
    preset = CITY_ENVIRONMENT_PRESETS.get(location, {})
    annual_temperature = _safe_float(requirement.get("annual_temperature"), preset.get("annual_temperature", 15.0))
    return {
        "annual_temperature": annual_temperature,
    }


def _derive_cooling_priority(requirement: dict[str, Any], environmental_data: dict[str, Any]) -> str:
    explicit_priority = str(requirement.get("priority") or "").strip()
    if explicit_priority:
        return explicit_priority

    density = _safe_float(requirement.get("computing_power_density"), 0.0)
    annual_temperature = _safe_float(environmental_data.get("annual_temperature"), 15.0)

    if annual_temperature <= 10.0 and density >= 15.0:
        return "green"
    if density >= 18.0:
        return "reliable"
    return "economic"


def _derive_facility_total_load_mw(requirement: dict[str, Any]) -> float:
    it_load_mw = _safe_float(requirement.get("planned_load_kw"), 0.0) / 1000.0
    pue_target = _safe_float(requirement.get("pue_target"), 1.25)
    if it_load_mw <= 0:
        return 0.0
    return round(it_load_mw * max(pue_target, 1.0), 4)


CITY_GREEN_STRATEGY_PRESETS: dict[str, dict[str, Any]] = {
    "\u4e4c\u5170\u5bdf\u5e03": {
        "resource_tier": "rich",
        "recommended_direct_ratio": 0.30,
        "green_power_purchase_share": 0.80,
        "green_power_premium_yuan_per_kwh": 0.03,
        "green_certificate_price_yuan_per_kwh": 0.015,
        "recommended_path": "local_green_power_trade_then_certificate",
    },
    "\u5f20\u5bb6\u53e3": {
        "resource_tier": "rich",
        "recommended_direct_ratio": 0.30,
        "green_power_purchase_share": 0.80,
        "green_power_premium_yuan_per_kwh": 0.03,
        "green_certificate_price_yuan_per_kwh": 0.015,
        "recommended_path": "local_green_power_trade_then_certificate",
    },
    "\u8d35\u9633": {
        "resource_tier": "moderate",
        "recommended_direct_ratio": 0.10,
        "green_power_purchase_share": 0.60,
        "green_power_premium_yuan_per_kwh": 0.04,
        "green_certificate_price_yuan_per_kwh": 0.018,
        "recommended_path": "provincial_green_power_trade_then_certificate",
    },
    "\u5317\u4eac": {
        "resource_tier": "load_center",
        "recommended_direct_ratio": 0.05,
        "green_power_purchase_share": 0.50,
        "green_power_premium_yuan_per_kwh": 0.05,
        "green_certificate_price_yuan_per_kwh": 0.020,
        "recommended_path": "interprovincial_green_power_trade_and_certificate",
    },
    "default": {
        "resource_tier": "moderate",
        "recommended_direct_ratio": 0.15,
        "green_power_purchase_share": 0.60,
        "green_power_premium_yuan_per_kwh": 0.04,
        "green_certificate_price_yuan_per_kwh": 0.018,
        "recommended_path": "green_power_trade_then_certificate",
    },
}


def _get_green_strategy_preset(location: str) -> dict[str, Any]:
    return dict(CITY_GREEN_STRATEGY_PRESETS.get((location or "").strip(), CITY_GREEN_STRATEGY_PRESETS["default"]))


def _derive_direct_connection_ratio(requirement: dict[str, Any]) -> tuple[float, float, bool]:
    total_ratio = max(0.0, min(1.0, _safe_float(requirement.get("green_power_ratio"), 0.0)))
    explicit_ratio = requirement.get("direct_connection_ratio")
    preset = _get_green_strategy_preset(str(requirement.get("location") or ""))
    recommended_ratio = max(0.0, min(total_ratio, _safe_float(preset.get("recommended_direct_ratio"), total_ratio)))
    if explicit_ratio is None:
        return recommended_ratio, recommended_ratio, True
    direct_ratio = max(0.0, min(total_ratio, _safe_float(explicit_ratio, recommended_ratio)))
    return direct_ratio, recommended_ratio, False


def _estimate_average_electricity_price(requirement: dict[str, Any]) -> float:
    prices = requirement.get("electricity_prices") or {}
    if isinstance(prices, dict):
        numeric_prices = [float(v) for v in prices.values() if isinstance(v, (int, float))]
        if numeric_prices:
            return sum(numeric_prices) / len(numeric_prices)
    return 0.45


def _build_green_procurement_plan(
    requirement: dict[str, Any],
    green_power_result: dict[str, Any],
    cooling_result: dict[str, Any],
    recommended_direct_ratio: float,
    auto_recommended: bool,
) -> dict[str, Any]:
    location = str(requirement.get("location") or "")
    preset = _get_green_strategy_preset(location)
    optimization = dict(green_power_result.get("optimization") or {})

    total_ratio = max(0.0, min(1.0, _safe_float(requirement.get("green_power_ratio"), 0.0)))
    actual_direct_ratio = max(
        0.0,
        min(
            total_ratio,
            _safe_float(
                optimization.get("green_supply_ratio"),
                _safe_float(requirement.get("direct_connection_ratio"), recommended_direct_ratio),
            ),
        ),
    )
    procured_ratio = max(0.0, round(total_ratio - actual_direct_ratio, 6))

    planned_load_kw = _safe_float(requirement.get("planned_load_kw"), 0.0)
    pue = _safe_float(cooling_result.get("estimated_pue"), _safe_float(requirement.get("pue_target"), 1.0))
    annual_total_energy_mwh = planned_load_kw * pue * 8760.0 / 1000.0
    annual_direct_green_energy_mwh = annual_total_energy_mwh * actual_direct_ratio
    annual_procured_green_energy_mwh = annual_total_energy_mwh * procured_ratio

    green_power_purchase_share = max(0.0, min(1.0, _safe_float(preset.get("green_power_purchase_share"), 0.6)))
    purchased_green_power_ratio = procured_ratio * green_power_purchase_share
    purchased_certificate_ratio = procured_ratio - purchased_green_power_ratio

    annual_green_power_trade_mwh = annual_total_energy_mwh * purchased_green_power_ratio
    annual_green_certificate_mwh = annual_total_energy_mwh * purchased_certificate_ratio

    green_power_premium = _safe_float(preset.get("green_power_premium_yuan_per_kwh"), 0.04)
    green_certificate_price = _safe_float(preset.get("green_certificate_price_yuan_per_kwh"), 0.018)
    annual_green_power_trade_cost_lakh = annual_green_power_trade_mwh * 1000.0 * green_power_premium / 10000.0
    annual_green_certificate_cost_lakh = annual_green_certificate_mwh * 1000.0 * green_certificate_price / 10000.0

    average_grid_price = _estimate_average_electricity_price(requirement)
    if procured_ratio <= 0:
        method = "none"
        method_label = "全部由绿电直连满足"
    elif purchased_green_power_ratio > 0 and purchased_certificate_ratio > 0:
        method = "hybrid"
        method_label = "绿电交易+绿证补足"
    elif purchased_green_power_ratio > 0:
        method = "green_power_trade"
        method_label = "绿电交易"
    else:
        method = "green_certificate"
        method_label = "绿证补足"

    summary = (
        f"Total green power target {total_ratio:.1%}; "
        f"direct connection {actual_direct_ratio:.1%}; "
        f"remaining {procured_ratio:.1%} via {method_label}."
    )

    return {
        "policy_mode": "direct_connection_plus_market_procurement",
        "resource_tier": preset.get("resource_tier", "moderate"),
        "recommended_path": preset.get("recommended_path", "green_power_trade_then_certificate"),
        "is_direct_ratio_auto_recommended": auto_recommended,
        "recommended_direct_connection_ratio": round(recommended_direct_ratio, 4),
        "actual_direct_connection_ratio": round(actual_direct_ratio, 4),
        "procured_green_ratio": round(procured_ratio, 4),
        "total_green_power_ratio": round(total_ratio, 4),
        "annual_total_energy_mwh": round(annual_total_energy_mwh, 2),
        "annual_direct_green_energy_mwh": round(annual_direct_green_energy_mwh, 2),
        "annual_procured_green_energy_mwh": round(annual_procured_green_energy_mwh, 2),
        "purchased_green_power_ratio": round(purchased_green_power_ratio, 4),
        "purchased_green_certificate_ratio": round(purchased_certificate_ratio, 4),
        "annual_green_power_trade_mwh": round(annual_green_power_trade_mwh, 2),
        "annual_green_certificate_mwh": round(annual_green_certificate_mwh, 2),
        "annual_green_power_trade_cost_lakh": round(annual_green_power_trade_cost_lakh, 2),
        "annual_green_certificate_cost_lakh": round(annual_green_certificate_cost_lakh, 2),
        "annual_procurement_cost_lakh": round(annual_green_power_trade_cost_lakh + annual_green_certificate_cost_lakh, 2),
        "average_grid_electricity_price_yuan_per_kwh": round(average_grid_price, 3),
        "green_power_premium_yuan_per_kwh": round(green_power_premium, 3),
        "green_certificate_price_yuan_per_kwh": round(green_certificate_price, 3),
        "method": method,
        "method_label": method_label,
        "policy_notes": [
            "并网型绿电直连项目应坚持以荷定源、自发自用、减少向公网反送。",
            "剩余绿电消费缺口可通过绿电交易或绿证进行市场化补足。",
            "绿电交易优先体现电能属性，绿证适合作为剩余绿色权益补足。",
        ],
        "summary": summary,
    }


def _calculate_annual_carbon_emission_tons(
    requirement: dict[str, Any],
    green_optimization: dict[str, Any],
    cooling_result: dict[str, Any],
) -> float:
    """Estimate annual carbon emission in tons using annual energy and total green-power ratio."""
    planned_load_kw = _safe_float(requirement.get("planned_load_kw"), 0.0)
    pue = _safe_float(cooling_result.get("estimated_pue"), _safe_float(requirement.get("pue_target"), 1.0))
    green_ratio = _safe_float(
        green_optimization.get("total_green_power_ratio"),
        _safe_float(
            green_optimization.get("green_supply_ratio"),
            _safe_float(requirement.get("green_power_ratio"), 0.0),
        ),
    )
    green_ratio = max(0.0, min(1.0, green_ratio))
    carbon_factor = _safe_float(requirement.get("carbon_emission_factor"), 0.0)

    annual_total_energy_mwh = planned_load_kw * pue * 8760.0 / 1000.0
    ratio_based_emission = annual_total_energy_mwh * (1.0 - green_ratio) * carbon_factor
    return round(ratio_based_emission, 2)


def _build_expert_analysis_context(state: GraphState) -> dict[str, Any]:
    requirement = dict(state.get("requirement") or {})
    green_power_result = dict(state.get("green_power_result") or {})
    cooling_result = dict(state.get("cooling_result") or {})
    power_supply_plan = dict(state.get("power_supply_plan") or {})
    cost_result = dict(state.get("economic_analysis_result") or {})

    green_optimization = dict(green_power_result.get("optimization") or {})
    green_procurement = dict(green_power_result.get("procurement_plan") or {})
    cooling_economic = dict(cooling_result.get("economic_indicators") or {})
    cooling_kpis = dict(cooling_result.get("cooling_kpis") or {})
    power_raw = dict(power_supply_plan.get("raw_json") or {})
    capex_breakdown = dict(cost_result.get("capex_breakdown") or {})

    rack_count = _estimate_rack_count(requirement)
    annual_carbon_emission = _calculate_annual_carbon_emission_tons(
        requirement=requirement,
        green_optimization=green_optimization,
        cooling_result=cooling_result,
    )

    return {
        "requirement": requirement,
        "draft_plan_summary": state.get("draft_plan_summary", ""),
        "cost_analysis": cost_result,
        "derived_metrics": {
            "rack_count": rack_count,
            "total_cost_lakh": _safe_float(cost_result.get("total_capex_lakh"), 0.0),
            "cost_per_rack_lakh": round(_safe_float(cost_result.get("total_capex_lakh"), 0.0) / rack_count, 2) if rack_count else 0.0,
            "budget_constraint_lakh": _safe_float(cost_result.get("budget_constraint_lakh"), _safe_float(requirement.get("budget_constraint"), 0.0)),
            "annual_carbon_emission_tons": round(annual_carbon_emission, 2),
        },
        "power_supply_plan": {
            **power_supply_plan,
            "raw_json": power_raw,
            "derived_metrics": {
                "tier_level": _machine_grade_to_tier(power_raw.get("machine_room_grade") or requirement.get("machine_room_grade")),
                "cost_per_mw": _safe_float(power_raw.get("cost_per_mw"), 0.0),
                "total_load_mw": _safe_float(power_raw.get("total_load_mw"), _safe_float(requirement.get("planned_load_kw"), 0.0) / 1000.0),
            },
        },
        "cooling_result": {
            **cooling_result,
            "economic_indicators": cooling_economic,
            "cooling_kpis": cooling_kpis,
            "derived_metrics": {
                "initial_investment_lakh": _safe_float(cooling_economic.get("initial_investment"), 0.0),
                "annual_op_cost_lakh": _safe_float(cooling_economic.get("annual_op_cost"), 0.0),
                "annual_electricity_cost_lakh": _safe_float(cooling_economic.get("annual_electricity_cost"), 0.0),
                "estimated_pue": _safe_float(cooling_result.get("estimated_pue"), _safe_float(requirement.get("pue_target"), 0.0)),
            },
        },
        "green_power_result": {
            **green_power_result,
            "optimization": green_optimization,
            "procurement_plan": green_procurement,
            "derived_metrics": {
                "wind_capacity_mw": _safe_float(green_optimization.get("wind_capacity_mw"), 0.0),
                "pv_capacity_mw": _safe_float(green_optimization.get("pv_capacity_mw"), 0.0),
                "storage_capacity_mwh": _safe_float(green_optimization.get("storage_capacity_mwh"), 0.0),
                "green_power_ratio": _safe_float(
                    green_procurement.get("total_green_power_ratio"),
                    _safe_float(
                        green_optimization.get("green_supply_ratio"),
                        _safe_float(requirement.get("green_power_ratio"), 0.0)
                    )
                ),
                "direct_connection_ratio": _safe_float(
                    green_procurement.get("actual_direct_connection_ratio"),
                    _safe_float(requirement.get("green_power_ratio"), 0.0)
                ),
                "procured_green_ratio": _safe_float(green_procurement.get("procured_green_ratio"), 0.0),
                "annual_carbon_emission_tons": round(annual_carbon_emission, 2),
                "annual_procurement_cost_lakh": _safe_float(green_procurement.get("annual_procurement_cost_lakh"), 0.0),
            },
        },
        "capex_breakdown": capex_breakdown,
    }


def _align_economic_opinion_data(opinion_data: dict[str, Any], state: GraphState) -> dict[str, Any]:
    context = _build_expert_analysis_context(state)
    metrics = dict(opinion_data.get("metrics") or {})
    derived = context["derived_metrics"]
    cost_analysis = context["cost_analysis"]
    total_cost = round(_safe_float(cost_analysis.get("total_capex_lakh"), derived["total_cost_lakh"]), 2)

    metrics["total_cost"] = total_cost
    metrics["cost_per_rack"] = derived["cost_per_rack_lakh"]
    metrics["budget_delta"] = round(_safe_float(cost_analysis.get("budget_delta_lakh"), 0.0), 2)
    metrics.setdefault("roi", metrics.get("roi", 0.0))
    metrics.setdefault("payback_period", metrics.get("payback_period", 0.0))

    aligned = dict(opinion_data)
    aligned["metrics"] = metrics
    aligned["summary"] = (
        f"Estimated total CAPEX is {total_cost:.2f} lakh yuan; "
        f"cost per rack is {derived['cost_per_rack_lakh']:.2f} lakh yuan; "
        f"{'currently over budget by ' + format(_safe_float(cost_analysis.get('budget_delta_lakh'), 0.0), '.2f') + ' lakh yuan' if cost_analysis.get('is_over_budget') else 'currently within budget'}."
    )
    return aligned


def _align_power_reliability_opinion_data(opinion_data: dict[str, Any], state: GraphState) -> dict[str, Any]:
    context = _build_expert_analysis_context(state)
    requirement = context["requirement"]
    power_plan = context["power_supply_plan"]
    power_derived = power_plan.get("derived_metrics", {})
    metrics = dict(opinion_data.get("metrics") or {})

    metrics["tier_level"] = int(power_derived.get("tier_level", 3))
    metrics["ups_configuration"] = power_plan.get("redundancy_logic") or power_plan.get("scheme_name") or metrics.get("ups_configuration", "")
    metrics["ups_capacity"] = round(_safe_float(requirement.get("planned_load_kw"), 0.0), 2)
    metrics["distribution_reliability"] = round(min(0.9999, 0.97 + 0.005 * metrics["tier_level"]), 4)
    if "expected_availability" not in metrics:
        metrics["expected_availability"] = {4: 99.995, 3: 99.982, 2: 99.75, 1: 99.0}.get(metrics["tier_level"], 99.982)
    if "annual_downtime" not in metrics:
        metrics["annual_downtime"] = round((1 - metrics["expected_availability"] / 100) * 8760, 2)

    aligned = dict(opinion_data)
    aligned["metrics"] = metrics
    aligned["summary"] = (
        f"Recommended reliability target is Tier {metrics['tier_level']}; "
        f"UPS / redundancy strategy: {metrics['ups_configuration']}; "
        f"external voltage level: {power_plan.get('external_voltage', 'unknown')}; "
        f"expected availability about {metrics['expected_availability']:.3f}%."
    )
    return aligned


def _align_environmental_opinion_data(opinion_data: dict[str, Any], state: GraphState) -> dict[str, Any]:
    context = _build_expert_analysis_context(state)
    requirement = context["requirement"]
    cooling = context["cooling_result"]
    green = context["green_power_result"]
    derived = context["derived_metrics"]
    metrics = dict(opinion_data.get("metrics") or {})
    rack_count = derived.get("rack_count", 0)

    metrics["pue_target"] = round(
        _safe_float(cooling.get("estimated_pue"), _safe_float(requirement.get("pue_target"), 0.0)),
        3,
    )
    procurement_plan = dict(green.get("procurement_plan") or {})
    metrics["green_power_ratio"] = round(
        _safe_float(
            procurement_plan.get("total_green_power_ratio"),
            _safe_float(green.get("optimization", {}).get("green_supply_ratio"), _safe_float(requirement.get("green_power_ratio"), 0.0)),
        ),
        4,
    )
    metrics["direct_connection_ratio"] = round(
        _safe_float(
            procurement_plan.get("actual_direct_connection_ratio"),
            _safe_float(green.get("optimization", {}).get("green_supply_ratio"), 0.0),
        ),
        4,
    )
    metrics["procured_green_ratio"] = round(_safe_float(procurement_plan.get("procured_green_ratio"), 0.0), 4)
    metrics["annual_carbon_emission"] = round(_safe_float(derived.get("annual_carbon_emission_tons"), 0.0), 2)
    metrics["carbon_per_rack"] = round(metrics["annual_carbon_emission"] / rack_count, 4) if rack_count else 0.0

    aligned = dict(opinion_data)
    aligned["metrics"] = metrics
    aligned["summary"] = (
        f"Estimated PUE is {metrics['pue_target']:.3f}; "
        f"total green power ratio is about {metrics['green_power_ratio']:.2%}; "
        f"annual carbon emission is about {metrics['annual_carbon_emission']:.2f} tons."
    )
    return aligned


class RequirementParserNode:
    """Requirement parsing node."""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """Parse and normalize the user requirement."""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Requirement Parser] Start working...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        raw_requirement = state.get("user_requirement") or state.get("requirement") or {}
        normalized = self._normalize_requirement(raw_requirement)
        try:
            parsed_requirement = UserRequirement(**normalized)
        except Exception as exc:
            raise ValueError(f"Invalid user requirement payload: {exc}") from exc

        parsed_dict = parsed_requirement.model_dump()

        sys.stdout.write("[OK] Requirement parsing completed\n")
        sys.stdout.write(f"  - Location: {parsed_dict.get('location', 'N/A')}\n")
        sys.stdout.write(f"  - Load: {parsed_dict.get('planned_load_kw', 'N/A')} kW\n")
        sys.stdout.write(f"  - Green ratio: {parsed_dict.get('green_power_ratio', 'N/A')}\n")
        sys.stdout.flush()

        # 璁板綍娴佸紡杈撳嚭
        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "requirement_parser",
            "expert": "Requirement Parser",
            "content": f"Requirements parsed: {parsed_dict.get('location', 'Unknown')}",
            "full_output": parsed_dict
        })

        return {
            "user_requirement": parsed_requirement,
            "requirement": parsed_dict,
            "current_step": "requirement_parsed",
            "streaming_output": streaming_output
        }

    def _normalize_requirement(self, raw: Any) -> dict[str, Any]:
        if hasattr(raw, "model_dump"):
            data = raw.model_dump()
        else:
            data = dict(raw or {})

        if "planned_load_kw" not in data:
            if "planned_load" in data:
                data["planned_load_kw"] = data["planned_load"]
            elif "total_power" in data:
                data["planned_load_kw"] = data["total_power"]

        if "green_power_ratio" not in data and "green_energy_target" in data:
            green_target = data.get("green_energy_target")
            if green_target is not None:
                data["green_power_ratio"] = float(green_target) / 100.0 if green_target > 1 else float(green_target)

        if "green_power_ratio" in data and data.get("green_power_ratio") is not None:
            total_ratio = float(data["green_power_ratio"])
            if total_ratio > 1:
                total_ratio = total_ratio / 100.0
            data["green_power_ratio"] = max(0.0, min(1.0, total_ratio))

        if "direct_connection_ratio" in data and data.get("direct_connection_ratio") is not None:
            direct_ratio = float(data["direct_connection_ratio"])
            if direct_ratio > 1:
                direct_ratio = direct_ratio / 100.0
            direct_ratio = max(0.0, min(1.0, direct_ratio))
            total_ratio = _safe_float(data.get("green_power_ratio"), 0.0)
            data["direct_connection_ratio"] = min(direct_ratio, total_ratio) if total_ratio > 0 else direct_ratio

        return data


class CostCalculationNode:
    """Cost calculation node."""

    def __call__(self, state: GraphState) -> dict[str, Any]:
        user_req = state.get("user_requirement")
        if hasattr(user_req, "model_dump"):
            user_req_data = user_req.model_dump()
        else:
            user_req_data = dict(user_req or {})

        green_power_result = state.get("green_power_result", {})
        cooling_result = state.get("cooling_result", {})
        power_supply_plan = state.get("power_supply_plan", {})
        budget_constraint = float(user_req_data.get("budget_constraint", 0.0) or 0.0)

        power_supply_raw = power_supply_plan.get("raw_json", {})
        load_mw = float(power_supply_raw.get("total_load_mw", 0.0) or 0.0)
        cost_per_mw = float(power_supply_raw.get("cost_per_mw", 0.0) or 0.0)
        power_supply_capex = load_mw * cost_per_mw

        optimization_res = green_power_result.get("optimization", {})
        procurement_plan = green_power_result.get("procurement_plan", {})
        wind_mw = float(optimization_res.get("wind_capacity_mw", 0.0) or 0.0)
        pv_mw = float(optimization_res.get("pv_capacity_mw", 0.0) or 0.0)
        storage_mwh = float(optimization_res.get("storage_capacity_mwh", 0.0) or 0.0)

        wind_capex = wind_mw * COST_FACTORS["wind_per_mw"]
        pv_capex = pv_mw * COST_FACTORS["pv_per_mw"]
        storage_capex = storage_mwh * COST_FACTORS["storage_per_mwh"]
        green_power_capex = wind_capex + pv_capex + storage_capex

        cooling_economic_indicators = cooling_result.get("economic_indicators", {})
        cooling_capex = float(cooling_economic_indicators.get("initial_investment", 0.0) or 0.0)

        total_capex = power_supply_capex + green_power_capex + cooling_capex
        is_over_budget = total_capex > budget_constraint
        budget_delta = total_capex - budget_constraint

        budget_retry_count = int(state.get("budget_retry_count", 0) or 0)
        max_budget_retries = int(state.get("max_budget_retries", 2) or 2)
        budget_feedback = ""
        if is_over_budget:
            budget_retry_count += 1
            budget_feedback = f"瓒呭嚭棰勭畻{budget_delta:.2f}涓囧厓锛岃閲嶆柊鍒跺畾鏂规"

        summary = (
            f"Estimated total CAPEX is {total_capex:.2f} lakh yuan. "
            f"Power supply CAPEX: {power_supply_capex:.2f} lakh yuan; "
            f"green power CAPEX: {green_power_capex:.2f} lakh yuan; "
            f"cooling CAPEX: {cooling_capex:.2f} lakh yuan. "
            f"Budget constraint: {budget_constraint:.2f} lakh yuan. "
        )
        if is_over_budget:
            summary += (
                f"Current plan exceeds budget by {budget_delta:.2f} lakh yuan. "
                "Recommendation: reduce the green power target, relax the power supply tier, or increase budget."
            )
        else:
            summary += f"Current plan remains within budget with {-budget_delta:.2f} lakh yuan headroom."

        analysis_result = {
            "status": "success",
            "is_over_budget": is_over_budget,
            "budget_constraint_lakh": budget_constraint,
            "total_capex_lakh": round(total_capex, 2),
            "budget_delta_lakh": round(budget_delta, 2),
            "budget_retry_count": budget_retry_count,
            "max_budget_retries": max_budget_retries,
            "budget_feedback": budget_feedback,
            "capex_breakdown": {
                "power_supply_system_lakh": round(power_supply_capex, 2),
                "green_power_system_lakh": round(green_power_capex, 2),
                "cooling_system_lakh": round(cooling_capex, 2),
                "details": {
                    "wind_capex_lakh": round(wind_capex, 2),
                    "pv_capex_lakh": round(pv_capex, 2),
                    "storage_capex_lakh": round(storage_capex, 2),
                    "cooling_initial_investment_lakh": round(cooling_capex, 2),
                },
            },
            "opex_breakdown": {
                "annual_green_procurement_cost_lakh": round(_safe_float(procurement_plan.get("annual_procurement_cost_lakh"), 0.0), 2),
                "annual_green_power_trade_cost_lakh": round(_safe_float(procurement_plan.get("annual_green_power_trade_cost_lakh"), 0.0), 2),
                "annual_green_certificate_cost_lakh": round(_safe_float(procurement_plan.get("annual_green_certificate_cost_lakh"), 0.0), 2),
            },
            "summary": summary,
            "cost_factors": COST_FACTORS,
        }

        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "cost_calculation",
            "expert": "Cost Calculation",
            "content": analysis_result["summary"],
            "full_output": analysis_result,
        })

        return {
            "economic_analysis_result": analysis_result,
            "budget_feedback": budget_feedback,
            "budget_retry_count": budget_retry_count,
            "max_budget_retries": max_budget_retries,
            "streaming_output": streaming_output,
        }


class DraftPlanAgentNode:
    """Draft plan generation node."""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory
        self.tools = [
            green_power_allocation_tool,
            cooling_scheme_generator_tool,
            power_supply_config_tool,
        ]
        self.system_prompt = (
            "You are a data center solution draft agent. "
            "You MUST use the tools to generate an initial plan. "
            "Use the tools in this order when possible: "
            "1) green_power_allocation, 2) cooling-scheme-generator, 3) power_supply_config. "
            "Return ONLY JSON with keys: green_power_result, cooling_result, power_supply_plan, summary."
        )

    def __call__(self, state: GraphState) -> dict[str, Any]:
        requirement = state.get("user_requirement") or {}
        if hasattr(requirement, "model_dump"):
            req_data = requirement.model_dump()
        else:
            req_data = dict(requirement)

        memory_context = self.memory.get_memory_context()
        budget_feedback = state.get("budget_feedback", "")
        draft_plan_feedback = state.get("draft_plan_feedback", "")

        if budget_feedback:
            sys.stdout.write(f"  - Budget feedback: {budget_feedback}\n")
        if draft_plan_feedback:
            sys.stdout.write("  - Debate feedback received\n")
        sys.stdout.write("=" * 60 + "\n")
        sys.stdout.flush()

        input_payload = {
            "user_requirement": req_data,
            "budget_feedback": budget_feedback,
            "debate_feedback": draft_plan_feedback,
            "memory_context": memory_context,
        }

        green_power_result = {}
        cooling_result = {}
        power_supply_plan = {}
        
        # 1. 璋冪敤缁跨數鍒嗛厤宸ュ叿
        try:
            sys.stdout.write("[Draft Plan Agent] Calling green_power_allocation...\n")
            sys.stdout.flush()
            direct_connection_ratio, recommended_direct_ratio, auto_recommended_direct_ratio = _derive_direct_connection_ratio(req_data)
            gp_input = {
                "location": req_data.get("location", "鍖椾含"),
                "green_power_ratio": direct_connection_ratio,
                "load_mw": float(req_data.get("planned_load_kw", 0)) / 1000,
                "sim_hours": req_data.get("sim_hours", 160),  # 浣跨敤鐢ㄦ埛閰嶇疆鎴栭粯璁?60灏忔椂
                "year": req_data.get("year", 2025),
            }
            for field in ("date", "pv_tilt", "pv_azimuth", "wind_cut_in_ms", "wind_rated_ms", "wind_cut_out_ms", "maxiter", "popsize", "seed"):
                value = req_data.get(field)
                if value not in (None, ""):
                    gp_input[field] = value
            print(f"[DraftPlanAgent] green_power_allocation input: {gp_input}", flush=True)
            temp_result = green_power_allocation_tool.invoke(gp_input)
            print(f"[DraftPlanAgent] green_power_allocation immediate result type: {type(temp_result)}", flush=True)
            print(f"[DraftPlanAgent] green_power_allocation immediate result keys: {list(temp_result.keys()) if isinstance(temp_result, dict) else 'not a dict'}", flush=True)
            if isinstance(temp_result, dict) and 'optimization' in temp_result:
                print(f"[DraftPlanAgent] optimization present in immediate result", flush=True)
                print(f"[DraftPlanAgent] pv_capacity_mw: {temp_result['optimization'].get('pv_capacity_mw')}", flush=True)
            elif isinstance(temp_result, dict) and 'cooling_technology' in temp_result:
                print(f"[DraftPlanAgent] WARNING: green_power_allocation returned cooling data!", flush=True)
            green_power_result = temp_result
            sys.stdout.write("[Draft Plan Agent] green_power_allocation completed\n")
            sys.stdout.flush()
        except Exception as e:
            print(f"[DraftPlanAgent] Error calling green_power_allocation: {e}", flush=True)
            import traceback
            print(f"[DraftPlanAgent] Traceback: {traceback.format_exc()}", flush=True)
            green_power_result = {
                "status": "error",
                "error_message": str(e),
                "error_type": type(e).__name__,
                "inputs": gp_input,
                "optimization": {},
                "generated_files": {},
                "pv_profile": {},
                "wind_profile": {},
            }
        
        # 2. 璋冪敤鍒跺喎鏂规宸ュ叿
        try:
            sys.stdout.write("[Draft Plan Agent] Calling cooling-scheme-generator...\n")
            sys.stdout.flush()
            environmental_data = _derive_environmental_data(req_data)
            cooling_priority = _derive_cooling_priority(req_data, environmental_data)
            cooling_input = {
                "user_requirements": req_data,
                "environmental_data": environmental_data,
                "location": req_data.get("location"),
                "planned_load": req_data.get("planned_load_kw"),
                "computing_power_density": req_data.get("computing_power_density", 8.0),
                "pue_target": req_data.get("pue_target", 1.3),
                "green_power_ratio": direct_connection_ratio,
                "priority": cooling_priority,
            }
            cooling_result = cooling_scheme_generator_tool.invoke(cooling_input)
            sys.stdout.write("[Draft Plan Agent] cooling-scheme-generator completed\n")
            sys.stdout.flush()
        except Exception as e:
            print(f"[DraftPlanAgent] Error calling cooling-scheme-generator: {e}", flush=True)
        
        # 3. 璋冪敤渚涚數閰嶇疆宸ュ叿
        try:
            sys.stdout.write("[Draft Plan Agent] Calling power_supply_config...\n")
            sys.stdout.flush()
            power_input = {
                "machine_room_grade": req_data.get("machine_room_grade", "A"),
                "total_load_mw": _derive_facility_total_load_mw(req_data),
                "pue_target": req_data.get("pue_target", 1.3),
            }
            power_supply_plan = power_supply_config_tool.invoke(power_input)
            sys.stdout.write("[Draft Plan Agent] power_supply_config completed\n")
            sys.stdout.flush()
        except Exception as e:
            print(f"[DraftPlanAgent] Error calling power_supply_config: {e}", flush=True)

        sys.stdout.write("[Draft Plan Agent] All tools completed\n")
        sys.stdout.flush()

        output_text = "{}"
        plan_data = {}
        
        # 宸ュ叿宸茬粡鐩存帴璋冪敤锛岀粨鏋滃凡缁忓湪 green_power_result, cooling_result, power_supply_plan 涓?        # 濡傛灉缁撴灉涓虹┖锛屽皾璇曚粠鐘舵€佷腑鑾峰彇缂撳瓨
        if not green_power_result:
            green_power_result = state.get("green_power_result", {})
        if not cooling_result:
            cooling_result = state.get("cooling_result", {})
        if not power_supply_plan:
            power_supply_plan = state.get("power_supply_plan", {})
        
        print(f"[DraftPlanAgent] green_power_result exists: {bool(green_power_result)}", flush=True)
        print(f"[DraftPlanAgent] cooling_result exists: {bool(cooling_result)}", flush=True)
        print(f"[DraftPlanAgent] power_supply_plan exists: {bool(power_supply_plan)}", flush=True)
        
        if green_power_result:
            print(f"[DraftPlanAgent] green_power_result has optimization: {'optimization' in green_power_result}", flush=True)
            if 'optimization' in green_power_result:
                opt_keys = list(green_power_result['optimization'].keys()) if isinstance(green_power_result['optimization'], dict) else 'not dict'
                print(f"[DraftPlanAgent] optimization keys: {opt_keys}", flush=True)
            else:
                print(f"[DraftPlanAgent] green_power_result keys: {list(green_power_result.keys())}", flush=True)
        if cooling_result:
            print(f"[DraftPlanAgent] cooling_result has cooling_technology: {'cooling_technology' in cooling_result}", flush=True)
            print(f"[DraftPlanAgent] cooling_result has cooling_kpis: {'cooling_kpis' in cooling_result}", flush=True)
            print(f"[DraftPlanAgent] cooling_result keys: {list(cooling_result.keys())}", flush=True)
        if power_supply_plan:
            print(f"[DraftPlanAgent] power_supply_plan has scheme_name: {'scheme_name' in power_supply_plan}", flush=True)
            print(f"[DraftPlanAgent] power_supply_plan has external_voltage: {'external_voltage' in power_supply_plan}", flush=True)
            print(f"[DraftPlanAgent] power_supply_plan keys: {list(power_supply_plan.keys())}", flush=True)

        green_optimization = green_power_result.get("optimization", {}) if isinstance(green_power_result, dict) else {}
        cooling_economic = cooling_result.get("economic_indicators", {}) if isinstance(cooling_result, dict) else {}
        power_raw = power_supply_plan.get("raw_json", {}) if isinstance(power_supply_plan, dict) else {}

        procurement_plan = _build_green_procurement_plan(
            req_data,
            green_power_result if isinstance(green_power_result, dict) else {},
            cooling_result if isinstance(cooling_result, dict) else {},
            recommended_direct_ratio,
            auto_recommended_direct_ratio,
        )
        if isinstance(green_power_result, dict):
            green_power_result["procurement_plan"] = procurement_plan
            if isinstance(green_optimization, dict):
                green_optimization["total_green_power_ratio"] = procurement_plan.get("total_green_power_ratio")
                green_optimization["direct_connection_ratio"] = procurement_plan.get("actual_direct_connection_ratio")
                green_optimization["procured_green_ratio"] = procurement_plan.get("procured_green_ratio")

        summary_parts = []
        if green_optimization:
            summary_parts.append(
                f"Green power: wind {green_optimization.get('wind_capacity_mw', 0):.2f} MW, "
                f"PV {green_optimization.get('pv_capacity_mw', 0):.2f} MW, "
                f"storage {green_optimization.get('storage_capacity_mwh', 0):.2f} MWh"
            )
        if procurement_plan.get("procured_green_ratio", 0) > 0:
            summary_parts.append(
                f"Green procurement: total {procurement_plan.get('total_green_power_ratio', 0):.2%}, "
                f"direct {procurement_plan.get('actual_direct_connection_ratio', 0):.2%}, "
                f"procured {procurement_plan.get('procured_green_ratio', 0):.2%}"
            )
        if cooling_result:
            summary_parts.append(
                f"Cooling: {cooling_result.get('cooling_technology', 'unknown')}, "
                f"PUE {cooling_result.get('estimated_pue', 0):.3f}, "
                f"CAPEX {cooling_economic.get('initial_investment', 0):.2f} lakh"
            )
        if power_supply_plan:
            summary_parts.append(
                f"Power: {power_supply_plan.get('scheme_name', 'unknown')}, "
                f"{power_supply_plan.get('external_voltage', 'unknown')}, "
                f"redundancy {power_supply_plan.get('redundancy_logic', 'unknown')}"
            )

        plan_summary = " | ".join(summary_parts) if summary_parts else "Draft plan generated"
        plan_data = {
            "summary": plan_summary,
            "green_power_result": green_power_result,
            "cooling_result": cooling_result,
            "power_supply_plan": power_supply_plan,
            "key_metrics": {
                "wind_capacity_mw": green_optimization.get("wind_capacity_mw"),
                "pv_capacity_mw": green_optimization.get("pv_capacity_mw"),
                "storage_capacity_mwh": green_optimization.get("storage_capacity_mwh"),
                "green_supply_ratio": green_optimization.get("green_supply_ratio"),
                "green_power_ratio": procurement_plan.get("total_green_power_ratio"),
                "direct_connection_ratio": procurement_plan.get("actual_direct_connection_ratio"),
                "procured_green_ratio": procurement_plan.get("procured_green_ratio"),
                "procurement_method": procurement_plan.get("method_label"),
                "annual_direct_green_energy_mwh": procurement_plan.get("annual_direct_green_energy_mwh"),
                "annual_procured_green_energy_mwh": procurement_plan.get("annual_procured_green_energy_mwh"),
                "annual_green_procurement_cost_lakh": procurement_plan.get("annual_procurement_cost_lakh"),
                "cooling_technology": cooling_result.get("cooling_technology") if isinstance(cooling_result, dict) else None,
                "estimated_pue": cooling_result.get("estimated_pue") if isinstance(cooling_result, dict) else None,
                "cooling_initial_investment_lakh": cooling_economic.get("initial_investment"),
                "power_scheme_name": power_supply_plan.get("scheme_name") if isinstance(power_supply_plan, dict) else None,
                "external_voltage": power_supply_plan.get("external_voltage") if isinstance(power_supply_plan, dict) else None,
                "power_cost_per_mw": power_raw.get("cost_per_mw") if isinstance(power_raw, dict) else None,
            },
        }

        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "draft_plan_agent",
            "expert": "Draft Plan Agent",
            "content": plan_summary,
            "full_output": {
                "raw_output": output_text,
                "parsed": plan_data,
                "green_power_result": green_power_result,
                "cooling_result": cooling_result,
                "power_supply_plan": power_supply_plan,
            },
        })

        # 璋冭瘯锛氭墦鍗板皢瑕佸彂閫佺殑鏁版嵁缁撴瀯
        print(f"[DraftPlanAgent] === FINAL OUTPUT DEBUG ===", flush=True)
        print(f"[DraftPlanAgent] green_power_result type: {type(green_power_result)}", flush=True)
        print(f"[DraftPlanAgent] green_power_result has optimization: {'optimization' in green_power_result}", flush=True)
        if 'optimization' in green_power_result:
            opt = green_power_result['optimization']
            print(f"[DraftPlanAgent] optimization keys: {list(opt.keys())}", flush=True)
            print(f"[DraftPlanAgent] pv_capacity_mw: {opt.get('pv_capacity_mw')}", flush=True)
            print(f"[DraftPlanAgent] wind_capacity_mw: {opt.get('wind_capacity_mw')}", flush=True)
            print(f"[DraftPlanAgent] storage_capacity_mwh: {opt.get('storage_capacity_mwh')}", flush=True)
            print(f"[DraftPlanAgent] achieved_green_ratio: {opt.get('achieved_green_ratio')}", flush=True)
        print(f"[DraftPlanAgent] cooling_result has cooling_technology: {'cooling_technology' in cooling_result}", flush=True)
        if 'cooling_technology' in cooling_result:
            print(f"[DraftPlanAgent] cooling_technology: {cooling_result['cooling_technology']}", flush=True)
            print(f"[DraftPlanAgent] estimated_pue: {cooling_result.get('estimated_pue')}", flush=True)
        print(f"[DraftPlanAgent] power_supply_plan has scheme_name: {'scheme_name' in power_supply_plan}", flush=True)
        if 'scheme_name' in power_supply_plan:
            print(f"[DraftPlanAgent] scheme_name: {power_supply_plan['scheme_name']}", flush=True)
            print(f"[DraftPlanAgent] external_voltage: {power_supply_plan.get('external_voltage')}", flush=True)
        print(f"[DraftPlanAgent] === END DEBUG ===", flush=True)

        return {
            "green_power_result": green_power_result,
            "cooling_result": cooling_result,
            "power_supply_plan": power_supply_plan,
            "draft_plan_summary": plan_summary,
            "streaming_output": streaming_output,
        }
    
    def _extract_tool_results_from_messages(self, result: dict, plan_data: dict) -> dict:
        """Extract tool results from agent messages and parsed data."""
        tool_results = {}
        
        messages = result.get("messages", [])
        for msg in messages:
            # 妫€鏌ユ槸鍚︽槸宸ュ叿璋冪敤缁撴灉
            tool_calls = getattr(msg, "tool_calls", None)
            tool_results_msg = getattr(msg, "tool_results", None)
            
            if tool_results_msg and isinstance(tool_results_msg, dict):
                for tool_name, tool_result in tool_results_msg.items():
                    if tool_result and isinstance(tool_result, dict):
                        tool_results[tool_name] = tool_result
            
            content = getattr(msg, "content", None)
            if content and isinstance(content, dict):
                if "green_power_allocation" in content:
                    tool_results["green_power_allocation"] = content["green_power_allocation"]
                if "cooling-scheme-generator" in content:
                    tool_results["cooling-scheme-generator"] = content["cooling-scheme-generator"]
                if "power_supply_config" in content:
                    tool_results["power_supply_config"] = content["power_supply_config"]
        
        print(f"[DraftPlanAgent] Extracted tool results from messages: {list(tool_results.keys())}", flush=True)
        
        if not tool_results and plan_data:
            print(f"[DraftPlanAgent] Trying to extract from plan_data, keys: {list(plan_data.keys())}", flush=True)
            if "optimization" in plan_data or "pv_profile" in plan_data or "wind_profile" in plan_data:
                tool_results["green_power_allocation"] = plan_data
                print(f"[DraftPlanAgent] Extracted green_power_allocation from plan_data", flush=True)
            if "cooling_technology" in plan_data:
                tool_results["cooling-scheme-generator"] = plan_data
                print(f"[DraftPlanAgent] Extracted cooling-scheme-generator from plan_data", flush=True)
            if "scheme_name" in plan_data:
                tool_results["power_supply_config"] = plan_data
                print(f"[DraftPlanAgent] Extracted power_supply_config from plan_data", flush=True)
        
        return tool_results

    def _parse_json_response(self, content: str) -> dict[str, Any]:
        import re

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {}

    def _extract_final_content(self, agent_result: dict[str, Any]) -> str:
        messages = agent_result.get("messages", [])
        for msg in reversed(messages):
            content = getattr(msg, "content", None)
            if isinstance(content, str) and content.strip():
                return content.strip()
        return ""

    def _on_stream_chunk(self, chunk: str):
        sys.stdout.write(chunk)
        sys.stdout.flush()


class ToolLoggingCallbackHandler(BaseCallbackHandler):
    """Log tool start/end for agent tool calls."""

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        name = serialized.get("name", "unknown")
        sys.stdout.write(f"[Tool] Starting: {name}\n")
        sys.stdout.flush()

    def on_tool_end(self, output: str, **kwargs) -> None:
        sys.stdout.write("[Tool] Completed\n")
        sys.stdout.flush()


class EconomicAnalysisNode:
    """Economic analysis node."""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an economic analysis expert for data center construction solutions.

Your expertise:
- Data center construction cost estimation
- Return on Investment (ROI) analysis
- Cost-benefit evaluation
- Budget control recommendations

Analysis points:
1. Total cost estimation (equipment, construction, operations)
2. Cost per rack analysis
3. Return on Investment calculation
4. Payback period estimation
5. Budget compliance evaluation
6. Cost optimization recommendations

Scoring standards (0-1 points):
- cost_efficiency: cost efficiency
- roi: return on investment

Output format:
Output in JSON format with EXACTLY these field names (do NOT translate to Chinese):
```json
{{
  "expert_type": "economic",
  "expert_name": "Economic Analysis Expert-Zhang",
  "summary": "Opinion summary",
  "reasoning": "Detailed reasoning process",
  "scores": {{
    "cost_efficiency": 0.85,
    "roi": 0.12
  }},
  "metrics": {{
    "total_cost": 1800,
    "cost_per_rack": 18,
    "roi": 0.12,
    "payback_period": 8
  }},
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "concerns": ["Concern 1"],
  "confidence": 0.85
}}
```

IMPORTANT:
- The numeric values in the JSON example above are placeholders only, NEVER copy them directly.
- Use EXACTLY the field names as shown above. Do not translate field names to Chinese.
- You can use Chinese for the field values, but field names MUST remain in English.
- You MUST base your analysis on the CURRENT workflow context JSON provided by the user, including the latest draft plan and cost calculation results.
"""),
            HumanMessage(content="Current workflow context JSON:\n{analysis_context}\nPlease conduct economic analysis in Chinese. Keep JSON field names in English.")
        ])

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """Run economic analysis."""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Economic Analysis Expert] Start analysis...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        memory_context = self.memory.get_memory_context()
        analysis_context = json.dumps(_build_expert_analysis_context(state), ensure_ascii=False, indent=2)

        # 鍒涘缓LLM
        llm = create_economic_llm(on_chunk=self._on_stream_chunk)

        # 鏋勫缓prompt
        base_prompt = self.prompt_template.format_messages(analysis_context=analysis_context)

        if memory_context:
            base_prompt.insert(
                -1,
                SystemMessage(content=f"[Previous discussion records]\n{memory_context}\n\nPlease refer to these discussion contents for your analysis. Keep JSON field names in English and use Chinese for textual values.")
            )

        # 璋冪敤LLM
        response = llm.invoke(base_prompt)

        # 瑙ｆ瀽杈撳嚭
        opinion_data = self._parse_json_response(response.content)
        opinion_data = _align_economic_opinion_data(opinion_data, state)
        opinion = ExpertOpinion(**opinion_data)

        self.memory.add_expert_opinion(
            expert_name=opinion.expert_name,
            expert_type=opinion.expert_type,
            opinion=opinion.summary
        )

        sys.stdout.write("\n[OK] Economic analysis completed\n")
        sys.stdout.write(f"  - Estimated cost: {opinion.metrics.get('total_cost', 'N/A')} wan yuan\n")
        sys.stdout.write(f"  - ROI: {opinion.scores.get('roi', 'N/A')*100:.1f}%\n")
        sys.stdout.write(f"  - Cost efficiency: {opinion.scores.get('cost_efficiency', 'N/A'):.2f}\n")
        sys.stdout.flush()

        # 璁板綍娴佸紡杈撳嚭
        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "economic_analysis",
            "expert": opinion.expert_name,
            "content": opinion.summary,
            "full_output": opinion.model_dump()
        })

        return {
            "economic_opinion": opinion,
            "streaming_output": streaming_output
        }

    def _parse_json_response(self, content: str) -> dict:
        """Parse JSON response."""
        import re

        # 棣栧厛灏濊瘯鐩存帴瑙ｆ瀽
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        # 灏濊瘯鎻愬彇JSON鍧楋紙澶勭悊markdown浠ｇ爜鍧楋級
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 灏濊瘯鐩存帴鏌ユ壘JSON瀵硅薄
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 灏濊瘯鏇村鏉傜殑JSON鎻愬彇锛堝鐞嗗祵濂楃粨鏋勶級
        stack = []
        start_idx = None
        for i, char in enumerate(content):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}' and stack:
                stack.pop()
                if not stack and start_idx is not None:
                    try:
                        json_str = content[start_idx:i+1]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

        sys.stderr.write(f"[WARN] Failed to parse JSON, using default values\n")
        return {
            "expert_type": "economic",
            "expert_name": "Economic Analysis Expert-Zhang",
            "summary": "Cost estimation completed",
            "reasoning": content[:500] if len(content) > 500 else content,
            "scores": {"cost_efficiency": 0.7, "roi": 0.1},
            "metrics": {},
            "recommendations": [],
            "concerns": [],
            "confidence": 0.6
        }

    def _on_stream_chunk(self, chunk: str):
        """Stream callback."""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class PowerReliabilityAnalysisNode:
    """Power reliability analysis node."""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a power reliability analysis expert for data center construction solutions.

Your expertise:
- Data center power system design
- UPS and redundancy configuration
- Tier standard compliance evaluation
- Power reliability analysis
- Risk assessment

Analysis points:
1. Determine power redundancy requirements based on Tier level
2. UPS capacity calculation and configuration
3. Power distribution architecture design (single bus/dual bus/redundant bus)
4. Expected availability calculation
5. Annual downtime estimation
6. Power risk assessment
7. Green power impact on reliability evaluation

Scoring standards (0-1 points):
- reliability: reliability score
- availability: availability score

Output format:
Output in JSON format with EXACTLY these field names (do NOT translate to Chinese):
```json
{{
  "expert_type": "power_reliability",
  "expert_name": "Power Reliability Expert-Li",
  "summary": "Opinion summary",
  "reasoning": "Detailed reasoning process",
  "scores": {{
    "reliability": 0.9,
    "availability": 0.9999
  }},
  "metrics": {{
    "tier_level": 3,
    "expected_availability": 99.98,
    "annual_downtime": 1.6,
    "ups_configuration": "2N UPS",
    "ups_capacity": 800,
    "distribution_reliability": 0.99
  }},
  "recommendations": ["Recommendation 1"],
  "concerns": ["Concern 1"],
  "confidence": 0.9
}}
```

IMPORTANT:
- The numeric values in the JSON example above are placeholders only, NEVER copy them directly.
- Use EXACTLY the field names as shown above. Do not translate field names to Chinese.
- You can use Chinese for the field values, but keep field names in English.
- You MUST base your analysis on the CURRENT workflow context JSON provided by the user, including the latest draft plan and cost calculation results.
"""),
            HumanMessage(content="Current workflow context JSON:\n{analysis_context}\nPlease conduct power reliability analysis in Chinese. Keep JSON field names in English.")
        ])

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """Run power reliability analysis."""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Power Reliability Expert] Start analysis...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        memory_context = self.memory.get_memory_context()
        analysis_context = json.dumps(_build_expert_analysis_context(state), ensure_ascii=False, indent=2)

        # 鍒涘缓LLM
        llm = create_power_reliability_llm(on_chunk=self._on_stream_chunk)

        # 鏋勫缓prompt
        base_prompt = self.prompt_template.format_messages(analysis_context=analysis_context)

        if memory_context:
            base_prompt.insert(
                -1,
                SystemMessage(content=f"[Previous discussion records]\n{memory_context}\n\nPlease refer to these discussion contents for your analysis. Keep JSON field names in English and use Chinese for textual values.")
            )

        # 璋冪敤LLM
        response = llm.invoke(base_prompt)

        # 瑙ｆ瀽杈撳嚭
        opinion_data = self._parse_json_response(response.content)
        opinion_data = _align_power_reliability_opinion_data(opinion_data, state)
        opinion = ExpertOpinion(**opinion_data)

        self.memory.add_expert_opinion(
            expert_name=opinion.expert_name,
            expert_type=opinion.expert_type,
            opinion=opinion.summary
        )

        sys.stdout.write("\n[OK] Power reliability analysis completed\n")
        sys.stdout.write(f"  - Expected availability: {opinion.metrics.get('expected_availability', 'N/A')}%\n")
        sys.stdout.write(f"  - Reliability score: {opinion.scores.get('reliability', 'N/A'):.2f}\n")
        sys.stdout.flush()

        # 璁板綍娴佸紡杈撳嚭
        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "power_reliability_analysis",
            "expert": opinion.expert_name,
            "content": opinion.summary,
            "full_output": opinion.model_dump()
        })

        return {
            "power_reliability_opinion": opinion,
            "streaming_output": streaming_output
        }

    def _parse_json_response(self, content: str) -> dict:
        """Parse JSON response."""
        import re

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        stack = []
        start_idx = None
        for i, char in enumerate(content):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}' and stack:
                stack.pop()
                if not stack and start_idx is not None:
                    try:
                        json_str = content[start_idx:i+1]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

        sys.stderr.write(f"[WARN] Failed to parse JSON, using default values\n")
        return {
            "expert_type": "power_reliability",
            "expert_name": "Power Reliability Expert-Li",
            "summary": "Reliability analysis completed",
            "reasoning": content[:500] if len(content) > 500 else content,
            "scores": {"reliability": 0.8, "availability": 0.999},
            "metrics": {},
            "recommendations": [],
            "concerns": [],
            "confidence": 0.7
        }

    def _on_stream_chunk(self, chunk: str):
        """Stream callback."""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class EnvironmentalAnalysisNode:
    """Environmental analysis node."""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an environmental analysis expert for data center construction solutions.

Your expertise:
- Carbon emission calculation and analysis
- PUE (Power Usage Effectiveness) evaluation
- Green power usage evaluation
- Environmental standard compliance
- Sustainable development recommendations

Analysis points:
1. PUE target evaluation (traditional >1.8, improved >1.5, efficient >1.3, ultra-efficient <=1.2)
2. Green power ratio evaluation (excellent >=80%, good >=60%, acceptable >=40%)
3. Annual carbon emission calculation
4. Cooling system environmental friendliness (refrigerant GWP value)
5. Carbon reduction potential analysis
6. Environmental optimization recommendations

Scoring standards (0-1 points):
- environmental_score: environmental score
- pue_score: PUE efficiency score
- green_power_score: green power usage score
- carbon_efficiency: carbon efficiency score

Output format:
Output in JSON format with EXACTLY these field names (do NOT translate to Chinese):
```json
{{
  "expert_type": "environmental",
  "expert_name": "Environmental Analysis Expert-Wang",
  "summary": "Opinion summary",
  "reasoning": "Detailed reasoning process",
  "scores": {{
    "environmental_score": 0.88,
    "pue_score": 0.95,
    "green_power_score": 0.9,
    "carbon_efficiency": 1.0
  }},
  "metrics": {{
    "pue_target": 1.3,
    "green_power_ratio": 0.7,
    "annual_carbon_emission": 250,
    "carbon_per_rack": 2.5
  }},
  "recommendations": ["Recommendation 1"],
  "concerns": ["Concern 1"],
  "confidence": 0.85
}}
```

IMPORTANT:
- The numeric values in the JSON example above are placeholders only, NEVER copy them directly.
- Use EXACTLY the field names as shown above. Do not translate field names to Chinese.
- You can use Chinese for the field values, but keep field names in English.
- You MUST base your analysis on the CURRENT workflow context JSON provided by the user, including the latest draft plan and cost calculation results.
"""),
            HumanMessage(content="Current workflow context JSON:\n{analysis_context}\nPlease conduct environmental analysis in Chinese. Keep JSON field names in English.")
        ])

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """Run environmental analysis."""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Environmental Analysis Expert] Start analysis...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        memory_context = self.memory.get_memory_context()
        analysis_context = json.dumps(_build_expert_analysis_context(state), ensure_ascii=False, indent=2)

        # 鍒涘缓LLM
        llm = create_environmental_llm(on_chunk=self._on_stream_chunk)

        # 鏋勫缓prompt
        base_prompt = self.prompt_template.format_messages(analysis_context=analysis_context)

        if memory_context:
            base_prompt.insert(
                -1,
                SystemMessage(content=f"[Previous discussion records]\n{memory_context}\n\nPlease refer to these discussion contents for your analysis. Keep JSON field names in English and use Chinese for textual values.")
            )

        # 璋冪敤LLM
        response = llm.invoke(base_prompt)

        # 瑙ｆ瀽杈撳嚭
        opinion_data = self._parse_json_response(response.content)
        opinion_data = _align_environmental_opinion_data(opinion_data, state)
        opinion = ExpertOpinion(**opinion_data)

        self.memory.add_expert_opinion(
            expert_name=opinion.expert_name,
            expert_type=opinion.expert_type,
            opinion=opinion.summary
        )

        sys.stdout.write("\n[OK] Environmental analysis completed\n")
        sys.stdout.write(f"  - Annual carbon emission: {opinion.metrics.get('annual_carbon_emission', 'N/A')} tons\n")
        sys.stdout.write(f"  - Environmental score: {opinion.scores.get('environmental_score', 'N/A'):.2f}\n")
        sys.stdout.flush()

        # 璁板綍娴佸紡杈撳嚭
        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "environmental_analysis",
            "expert": opinion.expert_name,
            "content": opinion.summary,
            "full_output": opinion.model_dump()
        })

        return {
            "environmental_opinion": opinion,
            "streaming_output": streaming_output
        }

    def _parse_json_response(self, content: str) -> dict:
        """Parse JSON response."""
        import re

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        stack = []
        start_idx = None
        for i, char in enumerate(content):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}' and stack:
                stack.pop()
                if not stack and start_idx is not None:
                    try:
                        json_str = content[start_idx:i+1]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

        sys.stderr.write(f"[WARN] Failed to parse JSON, using default values\n")
        return {
            "expert_type": "environmental",
            "expert_name": "Environmental Analysis Expert-Wang",
            "summary": "Environmental analysis completed",
            "reasoning": content[:500] if len(content) > 500 else content,
            "scores": {"environmental_score": 0.8, "pue_score": 0.8, "green_power_score": 0.8, "carbon_efficiency": 0.8},
            "metrics": {"pue_target": 1.5, "green_power_ratio": 0.5, "annual_carbon_emission": 0, "carbon_per_rack": 0},
            "recommendations": [],
            "concerns": [],
            "confidence": 0.7
        }

    def _on_stream_chunk(self, chunk: str):
        """Stream callback."""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class FinalReportNode:
    """Final report generation node."""

    def __call__(self, state: GraphState) -> dict[str, Any]:
        sys.stdout.write("\n" + "=" * 60 + "\n")
        sys.stdout.write("[Final Report] Start generating report...\n")
        sys.stdout.write("=" * 60 + "\n")
        sys.stdout.flush()

        state_payload = self._serialize_state(state)
        state_json = json.dumps(state_payload, ensure_ascii=False, indent=2)

        system_prompt = (
            "浣犳槸鈥滅豢鑹叉暟鎹腑蹇冭鍒掑彲琛屾€ф€婚【闂€濄€俓n\n"
            "宸ヤ綔鏂瑰紡锛堝繀椤婚伒瀹堬級锛歕n"
            "1. 鍏堥槄璇荤敤鎴锋彁渚涚殑 state_json锛岃瘑鍒凡缁欏嚭鐨勯」鐩弬鏁颁笌缂哄け瀛楁銆俓n"
            "2. 鍩轰簬 state 鏁版嵁鐩存帴瀹屾暣鍒嗘瀽锛屽苟鐢熸垚鏈€缁堟姤鍛娿€俓n"
            "3. 杈撳嚭鏈€缁堟姤鍛婃椂锛屽繀椤绘槸 Markdown 涓旀鏂囦笉灏戜簬 1000 瀛椼€俓n\n"
            "鎶ュ憡纭€ц姹傦細\n"
            "- 蹇呴』鍖呭惈缁撹锛氬彲琛?/ 鏈夋潯浠跺彲琛?/ 鏆備笉鍙銆俓n"
            "- 鑻ユ暟鎹己澶憋紝鏄庣‘鍐欏嚭鈥滄暟鎹己澶?寰呰ˉ鍏呪€濆強瀵圭粨璁哄奖鍝嶃€俓n\n"
            "寤鸿缁撴瀯锛歕n"
            "- 鏍囬涓庢憳瑕乗n"
            "- 1. 椤圭洰鑳屾櫙涓庣洰鏍囩害鏉焅n"
            "- 2. 鍦哄潃涓庣幆澧冨彲琛屾€n"
            "- 3. 鑳芥簮绯荤粺涓庣豢鐢垫秷绾崇瓥鐣n"
            "- 4. 鍒跺喎绯荤粺涓庤兘鏁堣矾寰刓n"
            "- 5. 浠跨湡缁撴灉瑙ｈ涓庤繍琛岀瓥鐣n"
            "- 6. 璐㈠姟鍙鎬т笌鎶曡祫鍥炴敹\n"
            "- 7. 椋庨櫓娓呭崟涓庣紦瑙ｆ帾鏂絓n"
            "- 8. 瀹炴柦璺嚎鍥撅紙杩戞湡/涓湡/杩滄湡锛塡n"
            "- 9. 缁煎悎缁撹涓庡缓璁甛n"
            "- 10. 鍏抽敭鎸囨爣姹囨€昏〃\n"
        )

        system_prompt = (
            "You are a senior data-center consulting partner writing the final Chinese deliverable for an owner/investor.\n"
            "Use the provided state_json as the only source of project facts. Do not invent exact values that are not in the data.\n"
            "Write in professional Chinese Markdown, with clear headings, tables, decision logic, assumptions, risks, and next-step actions.\n"
            "The report should feel like a formal consulting scheme report for a green data center, not a short AI summary.\n\n"
            "Mandatory quality requirements:\n"
            "1. Start with an executive decision page: recommendation, score, confidence, and key go/no-go conditions.\n"
            "2. Include project background, user inputs, capacity sizing, IT load, estimated rack count, PUE and green power targets.\n"
            "3. Explain the integrated technical architecture: cooling, power reliability, green power absorption, energy storage/procurement.\n"
            "4. Include economic analysis: CAPEX, OPEX, green-power cost, payback or cost-control logic when available.\n"
            "5. Include energy and carbon analysis: annual energy, green energy share, carbon impact when available.\n"
            "6. Include risk register with owner, trigger, impact, mitigation, and verification method.\n"
            "7. Include implementation roadmap by phase: design deepening, procurement, construction, commissioning, operation optimization.\n"
            "8. Include acceptance and monitoring KPIs: PUE, availability, green power ratio, carbon intensity, budget deviation.\n"
            "9. Use Markdown tables where possible. Keep prose concise but substantial.\n"
            "10. If information is missing, explicitly mark it as '待补充' and state why it matters.\n\n"
            "Recommended section outline:\n"
            "# 数据中心绿色供能与建设方案综合报告\n"
            "## 0. 执行结论与决策建议\n"
            "## 1. 项目概况与基础输入\n"
            "## 2. 设计边界、依据与关键假设\n"
            "## 3. 建设规模与容量测算\n"
            "## 4. 综合技术方案\n"
            "## 5. 经济性与全生命周期成本\n"
            "## 6. 能耗、绿电消纳与碳排分析\n"
            "## 7. 多专家评审与关键权衡\n"
            "## 8. 风险清单与缓释措施\n"
            "## 9. 实施路线、验收口径与后续工作\n"
            "## 10. 附录：关键指标表\n"
        )

        llm = create_final_report_llm()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"state_json:\n{state_json}")
        ]

        response = llm.invoke(messages)
        report_text = response.content.strip()
        report_text = self._ensure_project_overview_section(report_text, state_payload)
        report_text = self._ensure_consultant_depth_sections(report_text, state_payload)

        output_dir = Path(__file__).resolve().parents[1] / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = output_dir / f"final_report_{timestamp}.md"
        report_path.write_text(report_text, encoding="utf-8")

        solution = dict(state.get("solution") or {})
        solution.update({
            "final_report": report_text,
            "final_report_path": str(report_path),
        })

        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "final_report",
            "expert": "Final Report",
            "content": "Generated final feasibility report",
            "full_output": {"path": str(report_path)}
        })

        sys.stdout.write("[OK] Final report generated\n")
        sys.stdout.flush()

        return {
            "solution": solution,
            "streaming_output": streaming_output,
        }

    def _ensure_project_overview_section(self, report_text: str, state_payload: dict[str, Any]) -> str:
        if "## 项目概况与基础输入" in report_text:
            return report_text

        overview = self._build_project_overview_section(state_payload)
        if not overview:
            return report_text

        lines = report_text.splitlines()
        heading_index = next((idx for idx, line in enumerate(lines) if line.lstrip().startswith("#")), None)
        if heading_index is None:
            return f"{overview}\n\n{report_text}".strip()

        insert_at = heading_index + 1
        while insert_at < len(lines):
            current = lines[insert_at].strip()
            if not current or current.startswith("**"):
                insert_at += 1
                continue
            break

        new_lines = lines[:insert_at] + ["", overview, ""] + lines[insert_at:]
        return "\n".join(new_lines).strip()

    def _build_project_overview_section(self, state_payload: dict[str, Any]) -> str:
        requirement = state_payload.get("user_requirement") or {}
        if not isinstance(requirement, dict) or not requirement:
            return ""

        planned_load_kw = _safe_float(requirement.get("planned_load_kw"), 0.0)
        planned_area = _safe_float(requirement.get("planned_area"), 0.0)
        density = _safe_float(requirement.get("computing_power_density"), 0.0)
        green_ratio = _safe_float(requirement.get("green_power_ratio"), 0.0)
        direct_ratio = requirement.get("direct_connection_ratio")
        budget_constraint = _safe_float(requirement.get("budget_constraint"), 0.0)
        pue_target = _safe_float(requirement.get("pue_target"), 0.0)
        sim_hours = requirement.get("sim_hours")
        year = requirement.get("year")
        date = requirement.get("date")
        location = requirement.get("location") or "--"
        machine_room_grade = requirement.get("machine_room_grade") or "--"
        cooling_technology = requirement.get("cooling_technology") or "--"

        cabinet_count = round(planned_load_kw / density) if planned_load_kw > 0 and density > 0 else None
        load_summary = "--"
        if planned_load_kw > 0:
            load_summary = f"{self._format_number(planned_load_kw / 1000.0, 2)} MW ({self._format_number(planned_load_kw, 0)} kW)"

        rows = [
            ("项目地点", str(location)),
            ("建设规模", load_summary),
            ("规划建筑面积", f"{self._format_number(planned_area, 0)} m²" if planned_area > 0 else "--"),
            ("算力功率密度", f"{self._format_number(density, 2)} kW/柜" if density > 0 else "--"),
            ("估算机柜数量", f"{self._format_number(cabinet_count, 0)} 柜" if cabinet_count else "--"),
            ("机房等级", str(machine_room_grade)),
            ("制冷偏好", str(cooling_technology)),
            ("目标 PUE", self._format_number(pue_target, 2) if pue_target > 0 else "--"),
            ("绿电目标占比", self._format_percent(green_ratio)),
            ("绿电直连占比", self._format_percent(direct_ratio) if direct_ratio is not None else "未指定（可由系统推荐）"),
            ("预算约束", f"{self._format_number(budget_constraint, 0)} 万元" if budget_constraint > 0 else "--"),
            ("仿真参数", self._build_simulation_summary(sim_hours, year, date)),
        ]

        table = "\n".join(
            f"| {self._escape_markdown_cell(label)} | {self._escape_markdown_cell(value)} |"
            for label, value in rows
        )
        return "\n".join([
            "## 项目概况与基础输入",
            "",
            "以下内容直接来自用户在参数配置阶段提供的项目基础输入，用于说明本报告对应的数据中心建设画像与关键约束：",
            "",
            "| 项目 | 用户输入摘要 |",
            "| --- | --- |",
            table,
        ])

    def _build_simulation_summary(self, sim_hours: Any, year: Any, date: Any) -> str:
        parts: list[str] = []
        sim_hours_num = _safe_float(sim_hours, 0.0)
        if sim_hours_num > 0:
            parts.append(f"{self._format_number(sim_hours_num, 0)} 小时")
        if year:
            parts.append(f"{year} 年气象数据")
        if date:
            parts.append(f"指定日期 {date}")
        return "，".join(parts) if parts else "--"

    def _format_number(self, value: Any, digits: int = 0) -> str:
        number = _safe_float(value, float("nan"))
        if number != number:
            return "--"
        if digits <= 0:
            return f"{number:,.0f}"
        return f"{number:,.{digits}f}"

    def _format_percent(self, value: Any) -> str:
        ratio = _safe_float(value, float("nan"))
        if ratio != ratio:
            return "--"
        if ratio > 1:
            ratio = ratio / 100.0
        return f"{ratio * 100:.0f}%"

    def _escape_markdown_cell(self, value: Any) -> str:
        text = str(value if value not in (None, "") else "--")
        return text.replace("|", "\\|").replace("\n", "<br>")

    def _ensure_consultant_depth_sections(self, report_text: str, state_payload: dict[str, Any]) -> str:
        sections = self._build_consultant_depth_sections(state_payload)
        missing_sections = [
            section for heading, section in sections
            if heading.replace("## ", "") not in report_text
        ]
        if not missing_sections:
            return report_text
        return f"{report_text.rstrip()}\n\n" + "\n\n".join(missing_sections)

    def _build_consultant_depth_sections(self, state_payload: dict[str, Any]) -> list[tuple[str, str]]:
        requirement = self._as_dict(state_payload.get("user_requirement"))
        solution = self._as_dict(state_payload.get("solution"))
        cooling = self._as_dict(state_payload.get("cooling_result"))
        green = self._as_dict(state_payload.get("green_power_result"))
        power = self._as_dict(state_payload.get("power_supply_plan"))
        economic = self._as_dict(state_payload.get("economic_analysis_result"))

        return [
            ("## 设计边界、依据与关键假设", self._build_design_basis_section(requirement, power)),
            ("## 建设规模与容量测算", self._build_capacity_sizing_section(requirement, cooling, power)),
            ("## 综合技术方案深化", self._build_technical_scheme_section(cooling, green, power)),
            ("## 经济性与全生命周期成本", self._build_lifecycle_cost_section(requirement, economic, green, solution)),
            ("## 能耗、绿电消纳与碳排分析", self._build_energy_carbon_section(requirement, cooling, green, solution)),
            ("## 实施路线、验收口径与后续工作", self._build_delivery_section(solution)),
            ("## 附录：顾问复核清单", self._build_consultant_checklist_section(requirement, cooling, green, power, economic)),
        ]

    def _build_design_basis_section(self, requirement: dict[str, Any], power: dict[str, Any]) -> str:
        rows = [
            ("项目定位", "新建或扩建数据中心绿色供能与基础设施综合方案，当前报告用于方案比选、投资测算和深化设计输入。"),
            ("主要输入来源", "用户需求参数、制冷寻优结果、绿电容量优化、供电可靠性方案、经济性专家意见、多专家仲裁结果。"),
            ("机房等级口径", requirement.get("machine_room_grade") or "待补充"),
            ("供配电参考", power.get("standard_basis") or power.get("basis") or "GB 50174-2017、YD/T 5235-2019 等数据中心供配电设计口径，需在施工图阶段复核。"),
            ("能效边界", "PUE、绿电占比、碳排放因子按方案阶段测算，最终以全年实测和电力交易结算数据校核。"),
            ("投资边界", "CAPEX/OPEX 为方案阶段估算，未替代招标清单、施工图预算和设备厂家报价。"),
        ]
        return self._table_section(
            "## 设计边界、依据与关键假设",
            "本节明确报告的适用边界，避免将方案阶段测算误解为施工图或招标控制价。",
            ["边界项", "说明"],
            rows,
        )

    def _build_capacity_sizing_section(self, requirement: dict[str, Any], cooling: dict[str, Any], power: dict[str, Any]) -> str:
        planned_load_kw = _safe_float(requirement.get("planned_load_kw"), 0.0)
        density = _safe_float(requirement.get("computing_power_density"), 0.0)
        planned_area = _safe_float(requirement.get("planned_area"), 0.0)
        pue = _safe_float(cooling.get("estimated_pue"), _safe_float(requirement.get("pue_target"), 0.0))
        rack_count = round(planned_load_kw / density) if planned_load_kw > 0 and density > 0 else 0
        facility_load_kw = planned_load_kw * max(pue, 1.0) if planned_load_kw > 0 else 0
        annual_energy_mwh = facility_load_kw * 8760 / 1000 if facility_load_kw > 0 else 0
        area_density = planned_load_kw / planned_area if planned_area > 0 else 0
        rows = [
            ("IT 负荷规模", f"{self._format_number(planned_load_kw / 1000, 2)} MW" if planned_load_kw else "待补充"),
            ("估算机柜数量", f"{self._format_number(rack_count, 0)} 柜" if rack_count else "待补充"),
            ("单柜功率密度", f"{self._format_number(density, 2)} kW/柜" if density else "待补充"),
            ("建筑面积负荷密度", f"{self._format_number(area_density, 2)} kW/m²" if area_density else "待补充"),
            ("方案 PUE/目标 PUE", f"{self._format_number(pue, 3)} / {self._format_number(requirement.get('pue_target'), 3)}"),
            ("估算设施总负荷", f"{self._format_number(facility_load_kw / 1000, 2)} MW" if facility_load_kw else "待补充"),
            ("估算年用电量", f"{self._format_number(annual_energy_mwh, 0)} MWh/年" if annual_energy_mwh else "待补充"),
            ("供电接入电压", power.get("external_voltage") or power.get("voltage_level") or "待补充"),
        ]
        return self._table_section(
            "## 建设规模与容量测算",
            "容量测算用于校核制冷、供配电、绿电和投资估算是否在同一负荷边界下展开。",
            ["测算项", "方案值"],
            rows,
        )

    def _build_technical_scheme_section(self, cooling: dict[str, Any], green: dict[str, Any], power: dict[str, Any]) -> str:
        green_optimization = self._as_dict(green.get("optimization"))
        procurement = self._as_dict(green.get("procurement_plan"))
        rows = [
            ("制冷系统", cooling.get("cooling_technology") or cooling.get("strategy") or "待补充", "重点校核 PUE、WUE、余热回收和高密机柜适配能力。"),
            ("供配电系统", power.get("scheme_name") or power.get("name") or "待补充", f"外部电压：{power.get('external_voltage') or '待补充'}；冗余等级需与机房等级一致。"),
            ("绿电直连", self._format_percent(procurement.get("actual_direct_connection_ratio") or green_optimization.get("green_supply_ratio")), "直连比例应结合场址资源、并网条件和负荷曲线复核。"),
            ("绿电采购补足", procurement.get("method_label") or procurement.get("recommended_path") or "待补充", "建议同步配置绿电交易、绿证和碳核算台账。"),
            ("风光储容量", self._format_green_capacity(green_optimization), "容量结果应在全年 8760h 负荷曲线上复核弃电、缺口和储能循环次数。"),
            ("可运维性", "建议建立能源管理系统 EMS + DCIM 联动", "持续跟踪 PUE、绿电占比、碳排、储能 SOC 与关键设备健康状态。"),
        ]
        return self._table_section(
            "## 综合技术方案深化",
            "综合方案应把制冷、供电、绿电和运维监测视为一个系统，而不是三个孤立子方案。",
            ["系统", "推荐配置", "专业说明"],
            rows,
        )

    def _build_lifecycle_cost_section(
        self,
        requirement: dict[str, Any],
        economic: dict[str, Any],
        green: dict[str, Any],
        solution: dict[str, Any],
    ) -> str:
        key_metrics = self._as_dict(solution.get("key_metrics"))
        cost_breakdown = self._as_dict(solution.get("cost_breakdown"))
        capex_breakdown = self._as_dict(economic.get("capex_breakdown"))
        opex_breakdown = self._as_dict(economic.get("opex_breakdown"))
        procurement = self._as_dict(green.get("procurement_plan"))
        total_capex = (
            economic.get("total_capex_lakh")
            or solution.get("total_capex_lakh")
            or key_metrics.get("total_cost")
            or cost_breakdown.get("total")
        )
        rows = [
            ("预算约束", f"{self._format_number(requirement.get('budget_constraint'), 0)} 万元"),
            ("估算总 CAPEX", f"{self._format_number(total_capex, 0)} 万元" if _safe_float(total_capex, 0) else "待补充"),
            ("供电系统 CAPEX", f"{self._format_number(capex_breakdown.get('power_supply_system_lakh'), 0)} 万元" if capex_breakdown else "待补充"),
            ("绿电系统 CAPEX", f"{self._format_number(capex_breakdown.get('green_power_system_lakh'), 0)} 万元" if capex_breakdown else "待补充"),
            ("制冷系统 CAPEX", f"{self._format_number(capex_breakdown.get('cooling_system_lakh'), 0)} 万元" if capex_breakdown else "待补充"),
            ("年绿电交易成本", f"{self._format_number(procurement.get('annual_green_power_trade_cost_lakh'), 2)} 万元/年"),
            ("年绿证成本", f"{self._format_number(procurement.get('annual_green_certificate_cost_lakh'), 2)} 万元/年"),
            ("年运维成本", f"{self._format_number(opex_breakdown.get('annual_opex_lakh'), 2)} 万元/年" if opex_breakdown else "待补充"),
        ]
        return self._table_section(
            "## 经济性与全生命周期成本",
            "经济性判断不只看一次性投资，还应同时关注电费、绿电溢价、绿证成本、运维成本和未来扩容弹性。",
            ["成本项", "估算值"],
            rows,
        )

    def _build_energy_carbon_section(self, requirement: dict[str, Any], cooling: dict[str, Any], green: dict[str, Any], solution: dict[str, Any]) -> str:
        procurement = self._as_dict(green.get("procurement_plan"))
        key_metrics = self._as_dict(solution.get("key_metrics"))
        planned_load_kw = _safe_float(requirement.get("planned_load_kw"), 0.0)
        pue = _safe_float(cooling.get("estimated_pue"), _safe_float(requirement.get("pue_target"), 0.0))
        annual_energy = _safe_float(procurement.get("annual_total_energy_mwh"), 0.0)
        if annual_energy <= 0 and planned_load_kw > 0 and pue > 0:
            annual_energy = planned_load_kw * pue * 8760 / 1000
        green_ratio = _safe_float(
            procurement.get("total_green_power_ratio"),
            _safe_float(key_metrics.get("green_power_ratio"), _safe_float(requirement.get("green_power_ratio"), 0.0)),
        )
        carbon_factor = _safe_float(requirement.get("carbon_emission_factor"), 0.0)
        residual_grid_energy = annual_energy * max(0.0, 1.0 - green_ratio)
        residual_emission = residual_grid_energy * carbon_factor
        rows = [
            ("估算年总用电量", f"{self._format_number(annual_energy, 0)} MWh/年" if annual_energy else "待补充"),
            ("目标绿电占比", self._format_percent(green_ratio)),
            ("直连绿电电量", f"{self._format_number(procurement.get('annual_direct_green_energy_mwh'), 0)} MWh/年"),
            ("市场化绿电/绿证补足", f"{self._format_number(procurement.get('annual_procured_green_energy_mwh'), 0)} MWh/年"),
            ("剩余网电电量", f"{self._format_number(residual_grid_energy, 0)} MWh/年" if annual_energy else "待补充"),
            ("电网排放因子", f"{self._format_number(carbon_factor, 3)} tCO2/MWh" if carbon_factor else "待补充"),
            ("剩余范围二排放", f"{self._format_number(residual_emission, 0)} tCO2/年" if annual_energy and carbon_factor else "待补充"),
        ]
        return self._table_section(
            "## 能耗、绿电消纳与碳排分析",
            "本节将能耗、绿电消纳和碳排放放在同一张账中，便于后续 ESG 披露和运营考核。",
            ["指标", "测算值"],
            rows,
        )

    def _build_delivery_section(self, solution: dict[str, Any]) -> str:
        risks = solution.get("risks") if isinstance(solution.get("risks"), list) else []
        risk_summary = "；".join(
            str(item.get("description") or item.get("type") or item) for item in risks[:3]
            if item
        ) or "待在深化设计阶段形成正式风险台账"
        rows = [
            ("方案深化", "复核负荷边界、机柜密度、供电接入条件、绿电交易路径和全年气象/负荷曲线。"),
            ("初步设计", "形成总图、供配电一次方案、制冷系统图、能源站边界、EMS/DCIM 接口和投资估算。"),
            ("招采与施工图", "锁定设备参数、冗余策略、施工图预算、招标技术规格书和交付责任边界。"),
            ("施工与调试", "完成单机调试、系统联调、带载测试、PUE 初测、绿电计量链路验证。"),
            ("运营优化", "按月跟踪 PUE、绿电占比、碳排强度、储能利用率和预算偏差，形成持续优化闭环。"),
            ("当前重点风险", risk_summary),
        ]
        return self._table_section(
            "## 实施路线、验收口径与后续工作",
            "建议将本报告作为下一阶段设计任务书和专项复核清单的输入，而不是作为最终施工依据。",
            ["阶段", "关键工作"],
            rows,
        )

    def _build_consultant_checklist_section(
        self,
        requirement: dict[str, Any],
        cooling: dict[str, Any],
        green: dict[str, Any],
        power: dict[str, Any],
        economic: dict[str, Any],
    ) -> str:
        rows = [
            ("负荷边界", "IT 负荷、PUE、机柜密度、建筑面积是否一致", "已形成" if requirement else "待补充"),
            ("制冷路线", "是否输出 PUE/WUE/制冷功耗/余热回收指标", "已形成" if cooling else "待补充"),
            ("供电可靠性", "是否明确电压等级、冗余结构、等级依据", "已形成" if power else "待补充"),
            ("绿电消纳", "是否明确直连、交易、绿证、储能容量和年度电量", "已形成" if green else "待补充"),
            ("经济性", "是否有 CAPEX/OPEX、预算约束和成本敏感项", "已形成" if economic else "待补充"),
            ("验收指标", "是否可被后续监测系统持续采集", "需在施工图和运维平台阶段落表"),
        ]
        return self._table_section(
            "## 附录：顾问复核清单",
            "以下清单用于判断报告是否具备进入深化设计和投资评审的基本完整度。",
            ["复核项", "检查内容", "当前状态"],
            rows,
        )

    def _table_section(self, heading: str, lead: str, headers: list[str], rows: list[tuple[Any, ...]]) -> str:
        table = [
            "| " + " | ".join(self._escape_markdown_cell(header) for header in headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
        ]
        for row in rows:
            values = list(row)[:len(headers)]
            values.extend([""] * (len(headers) - len(values)))
            table.append("| " + " | ".join(self._escape_markdown_cell(value) for value in values) + " |")
        return "\n".join([heading, "", lead, "", *table])

    def _as_dict(self, value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if isinstance(value, dict):
            return value
        return {}

    def _format_green_capacity(self, optimization: dict[str, Any]) -> str:
        parts = []
        wind = _safe_float(optimization.get("wind_capacity_mw"), 0.0)
        pv = _safe_float(optimization.get("pv_capacity_mw"), 0.0)
        storage = _safe_float(optimization.get("storage_capacity_mwh"), 0.0)
        if wind > 0:
            parts.append(f"风电 {self._format_number(wind, 2)} MW")
        if pv > 0:
            parts.append(f"光伏 {self._format_number(pv, 2)} MWp")
        if storage > 0:
            parts.append(f"储能 {self._format_number(storage, 2)} MWh")
        return "；".join(parts) if parts else "待补充"

    def _serialize_state(self, state: GraphState) -> dict[str, Any]:
        def _dump(value: Any) -> Any:
            if hasattr(value, "model_dump"):
                return value.model_dump()
            return value

        return {
            "user_requirement": _dump(state.get("user_requirement")),
            "solution": state.get("solution"),
            "power_supply_plan": state.get("power_supply_plan"),
            "green_power_result": state.get("green_power_result"),
            "cooling_result": state.get("cooling_result"),
            "economic_analysis_result": state.get("economic_analysis_result"),
            "economic_opinion": _dump(state.get("economic_opinion")),
            "power_reliability_opinion": _dump(state.get("power_reliability_opinion")),
            "environmental_opinion": _dump(state.get("environmental_opinion")),
            "consensus_score": state.get("consensus_score"),
            "debate_round": state.get("debate_round"),
        }

    def _parse_json_response(self, content: str) -> dict:
        """Parse JSON response."""
        import re

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        stack = []
        start_idx = None
        for i, char in enumerate(content):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}' and stack:
                stack.pop()
                if not stack and start_idx is not None:
                    try:
                        json_str = content[start_idx:i+1]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

        sys.stderr.write(f"[WARN] Failed to parse JSON, using default values\n")
        return {
            "expert_type": "environmental",
            "expert_name": "Environmental Analysis Expert-Wang",
            "summary": "Environmental analysis completed",
            "reasoning": content[:500] if len(content) > 500 else content,
            "scores": {"environmental_score": 0.8, "pue_score": 0.8, "green_power_score": 0.8, "carbon_efficiency": 0.8},
            "metrics": {},
            "recommendations": [],
            "concerns": [],
            "confidence": 0.7
        }

    def _on_stream_chunk(self, chunk: str):
        """Stream callback."""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class DebateRoundNode:
    """Debate round node."""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """Run one debate round."""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write(f"[Debate Round {state['debate_round']}] Start...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        # 鑾峰彇涓撳鎰忚
        economic_opinion = state.get("economic_opinion")
        power_opinion = state.get("power_reliability_opinion")
        environmental_opinion = state.get("environmental_opinion")

        if not all([economic_opinion, power_opinion, environmental_opinion]):
            sys.stdout.write("[SKIP] Expert opinions incomplete, skip debate\n")
            return {
                "should_continue_debate": False,
                "consensus_reached": True
            }

        # 缁勭粐杞祦鍙戣█
        streaming_output = state.get("streaming_output", [])
        debate_history = list(state.get("debate_history", []))
        round_messages = []

        self._expert_speak(
            speaker=economic_opinion.expert_name,
            state=state,
            streaming_output=streaming_output,
            debate_history=debate_history,
            round_messages=round_messages,
            current_opinion=economic_opinion,
            other_opinions=[power_opinion, environmental_opinion]
        )

        self._expert_speak(
            speaker=power_opinion.expert_name,
            state=state,
            streaming_output=streaming_output,
            debate_history=debate_history,
            round_messages=round_messages,
            current_opinion=power_opinion,
            other_opinions=[economic_opinion, environmental_opinion]
        )

        self._expert_speak(
            speaker=environmental_opinion.expert_name,
            state=state,
            streaming_output=streaming_output,
            debate_history=debate_history,
            round_messages=round_messages,
            current_opinion=environmental_opinion,
            other_opinions=[economic_opinion, power_opinion]
        )

        consensus_score = self._evaluate_consensus(state)

        sys.stdout.write(f"\n[OK] Debate round {state['debate_round']} completed\n")
        sys.stdout.write(f"  - Consensus score: {consensus_score:.2f}\n")
        sys.stdout.flush()

        draft_plan_feedback = self.memory.get_memory_context()
        debate_summary = {
            "round": state["debate_round"],
            "messages": round_messages,
            "consensus_score": consensus_score,
            "suggestions": [
                f"Economic view: {economic_opinion.summary}",
                f"Reliability view: {power_opinion.summary}",
                f"Environmental view: {environmental_opinion.summary}",
            ],
            "message_count": len(round_messages),
        }
        streaming_output.append({
            "node": "debate_round",
            "expert": "Debate Coordinator",
            "content": f"绗?{state['debate_round']} 杞京璁哄畬鎴愶紝鍏?{len(round_messages)} 鏉″彂瑷€锛屽叡璇嗗害 {consensus_score:.2f}",
            "full_output": debate_summary,
        })

        return {
            "debate_round": state["debate_round"] + 1,
            "consensus_score": consensus_score,
            "should_continue_debate": consensus_score < 0.8,
            "consensus_reached": consensus_score >= 0.8,
            "draft_plan_feedback": draft_plan_feedback,
            "debate_history": debate_history,
            "streaming_output": streaming_output
        }

    def _expert_speak(
        self,
        speaker: str,
        state: GraphState,
        streaming_output: list,
        debate_history: list,
        round_messages: list,
        current_opinion: ExpertOpinion,
        other_opinions: list[ExpertOpinion]
    ):
        """Generate an expert statement."""
        sys.stdout.write(f"\n[{speaker} speaking...]\n")
        sys.stdout.flush()

        # 鏋勫缓prompt
        other_opinions_text = "\n".join([
            f"- {op.expert_name}: {op.summary}"
            for op in other_opinions
        ])

        prompt = f"""You are {speaker}, a data center construction solution design expert.

Your main point:
{current_opinion.summary}

Reasoning:
{current_opinion.reasoning}

Other experts' points:
{other_opinions_text}

[Debate task]
Now please express your opinion, focusing on:
1. Respond to other experts' points
2. State what you agree or disagree with reasons
3. Propose possible coordination solutions
4. Reveal trade-offs between different dimensions

Please respond concisely in Chinese, within 200 characters."""

        # 鍒涘缓LLM
        from greendatacenter.llm.config import get_llm
        llm = get_llm(
            temperature=0.6,
            max_tokens=300,
            on_chunk=self._on_stream_chunk,
            timeout=30
        )

        # 璋冪敤LLM
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content="You are a data center construction solution design debate expert."),
            HumanMessage(content=prompt)
        ]

        response = llm.invoke(messages)
        opinion = response.content.strip()

        sys.stdout.write(f"{speaker}: {opinion}\n")
        sys.stdout.flush()

        self.memory.add_debate_message(
            speaker=speaker,
            listener=None,
            message=opinion,
            message_type="statement"
        )

        # 璁板綍娴佸紡杈撳嚭
        message_payload = {
            "speaker": speaker,
            "content": opinion,
            "round": state["debate_round"]
        }
        debate_history.append(message_payload)
        round_messages.append(message_payload)
        streaming_output.append({
            "node": "debate_round",
            **message_payload
        })

    def _evaluate_consensus(self, state: GraphState) -> float:
        """Evaluate consensus."""
        economic_score = state.get("economic_opinion")
        power_score = state.get("power_reliability_opinion")
        environmental_score = state.get("environmental_opinion")

        if not all([economic_score, power_score, environmental_score]):
            return 0.5

        # 鎻愬彇涓昏璇勫垎
        econ_main = self._extract_main_score(economic_score.scores)
        power_main = self._extract_main_score(power_score.scores)
        env_main = self._extract_main_score(environmental_score.scores)

        scores = [econ_main, power_main, env_main]
        mean_score = sum(scores) / len(scores)

        # 璁＄畻鏍囧噯宸綔涓哄垎姝у害
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        divergence = variance ** 0.5

        consensus = max(0, min(1, 1 - divergence))

        return consensus

    def _extract_main_score(self, scores: dict) -> float:
        """Extract primary scores."""
        if not scores:
            return 0.5

        preferred_keys = [
            "reliability",
            "availability",
            "environmental_score",
            "cost_efficiency",
            "green_power_score",
            "pue_score",
            "carbon_efficiency",
            "roi",
        ]
        for key in preferred_keys:
            if key in scores:
                return _normalize_score_value(scores.get(key))

        # 鍥為€€锛氬彇绗竴涓彲瑙ｆ瀽鐨勬暟鍊艰瘎鍒嗭紝骞剁粺涓€褰掍竴鍖栧埌 0-1
        for value in scores.values():
            try:
                return _normalize_score_value(value)
            except (TypeError, ValueError):
                continue

        return 0.5

    def _on_stream_chunk(self, chunk: str):
        """Stream callback."""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class ArbitratorNode:
    """Arbitration node."""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """Run arbitration and finalize the solution."""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Arbitrator] Start comprehensive analysis...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        economic_opinion = state.get("economic_opinion")
        power_opinion = state.get("power_reliability_opinion")
        environmental_opinion = state.get("environmental_opinion")
        debate_round = state.get("debate_round", 0)
        
        # 鑾峰彇鎴愭湰璁＄畻缁撴灉锛堢敤浜庢纭殑鎬绘垚鏈級
        economic_analysis_result = state.get("economic_analysis_result", {})
        total_capex_lakh = economic_analysis_result.get("total_capex_lakh", 0)

        # 鏋勫缓浠茶prompt
        opinions_text = f"""
[Economic Analysis Expert-{economic_opinion.expert_name}]
Summary: {economic_opinion.summary}
Reasoning: {economic_opinion.reasoning}
Scores: {economic_opinion.scores}
Key metrics: {economic_opinion.metrics}
Recommendations: {economic_opinion.recommendations}

[Power Reliability Expert-{power_opinion.expert_name}]
Summary: {power_opinion.summary}
Reasoning: {power_opinion.reasoning}
Scores: {power_opinion.scores}
Key metrics: {power_opinion.metrics}
Recommendations: {power_opinion.recommendations}

[Environmental Analysis Expert-{environmental_opinion.expert_name}]
Summary: {environmental_opinion.summary}
Reasoning: {environmental_opinion.reasoning}
Scores: {environmental_opinion.scores}
Key metrics: {environmental_opinion.metrics}
Recommendations: {environmental_opinion.recommendations}

[Debate status]
Completed {debate_round} rounds of debate

[Cost Calculation]
Total CAPEX (project total investment): {total_capex_lakh} 涓囧厓
"""

        prompt = f"""You are a data center construction solution arbitrator.

Your task is to synthesize opinions from economic, power reliability, and environmental analysis experts to generate the final construction solution.

{opinions_text}

[Arbitration task]
1. Analyze consistency and disagreements among expert opinions
2. Balance conflicts between different dimensions
3. Generate optimal solution that accommodates multi-party requirements
4. Clarify final solution's overall scores and key metrics

Output format requirements (JSON) with EXACTLY these field names (do NOT translate to Chinese):
```json
{{
  "name": "Solution name",
  "summary": "Solution summary",
  "overall_scores": {{
    "economic": 0.85,
    "reliability": 0.9,
    "environmental": 0.88,
    "overall": 0.88
  }},
  "key_metrics": {{
    "total_cost": 1800,
    "pue": 1.3,
    "green_power_ratio": 0.7,
    "tier_level": 3,
    "expected_availability": 99.98,
    "annual_carbon_emission": 250
  }},
  "economic_section": {{
    "description": "Economic solution description",
    "content": {{"total_cost": 1800, "roi": 0.12}},
    "recommendations": ["Recommendation 1"]
  }},
  "power_reliability_section": {{
    "description": "Power reliability solution description",
    "content": {{"tier_level": 3, "ups_configuration": "2N"}},
    "recommendations": ["Recommendation 1"]
  }},
  "environmental_section": {{
    "description": "Environmental solution description",
    "content": {{"pue": 1.3, "green_power_ratio": 0.7}},
    "recommendations": ["Recommendation 1"]
  }},
  "trade_offs": [
    {{"conflict": "Cost vs Reliability", "resolution": "Prioritize reliability with optimization"}}
  ],
  "risks": [
    {{"type": "Power supply", "description": "Risk description"}}
  ],
  "recommendations": [
    "Final recommendation 1",
    "Final recommendation 2"
  ],
  "confidence": 0.85
}}
```

IMPORTANT: Use EXACTLY the field names as shown above. Do not translate field names to Chinese. You can use Chinese for the values, but keep field names in English.

Please conduct arbitration decision and generate final solution."""

        # 鍒涘缓LLM
        llm = create_arbitrator_llm(on_chunk=self._on_stream_chunk)

        # 璋冪敤LLM
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content="You are a data center construction solution design arbitrator."),
            HumanMessage(content=prompt)
        ]

        response = llm.invoke(messages)

        # 瑙ｆ瀽杈撳嚭
        solution_data = self._parse_json_response(response.content)
        solution_data = self._align_total_cost(solution_data, total_capex_lakh, state)

        sys.stdout.write("\n[OK] Arbitration decision completed\n")
        sys.stdout.write(f"  - Overall score: {solution_data.get('overall_scores', {}).get('overall', 0):.2f}\n")
        sys.stdout.write(f"  - Confidence: {solution_data.get('confidence', 0.8):.2f}\n")
        sys.stdout.flush()

        # 璁板綍娴佸紡杈撳嚭
        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "arbitrator",
            "expert": "Arbitrator",
            "content": "Generated final construction solution",
            "full_output": solution_data
        })

        return {
            "solution": solution_data,
            "streaming_output": streaming_output
        }

    def _align_total_cost(self, solution_data: dict, total_capex_lakh: float, state: GraphState) -> dict:
        """Align arbitrator output with workflow metrics."""
        normalized = dict(solution_data or {})
        total_cost = round(float(total_capex_lakh or 0.0), 2)
        economic_opinion = state.get("economic_opinion")
        economic_metrics = dict(getattr(economic_opinion, "metrics", {}) or {})
        power_opinion = state.get("power_reliability_opinion")
        power_metrics = dict(getattr(power_opinion, "metrics", {}) or {})
        environmental_opinion = state.get("environmental_opinion")
        environmental_metrics = dict(getattr(environmental_opinion, "metrics", {}) or {})
        roi = _safe_float(economic_metrics.get("roi"), 0.0)
        payback_period = _safe_float(economic_metrics.get("payback_period"), 0.0)

        key_metrics = dict(normalized.get("key_metrics") or {})
        key_metrics["total_cost"] = total_cost
        key_metrics["pue"] = round(
            _safe_float(
                environmental_metrics.get("pue"),
                _safe_float(environmental_metrics.get("pue_target"), key_metrics.get("pue", 0.0)),
            ),
            3,
        )
        key_metrics["green_power_ratio"] = round(
            _safe_float(environmental_metrics.get("green_power_ratio"), key_metrics.get("green_power_ratio", 0.0)),
            4,
        )
        key_metrics["tier_level"] = int(_safe_float(power_metrics.get("tier_level"), key_metrics.get("tier_level", 3)))
        key_metrics["expected_availability"] = round(
            _safe_float(power_metrics.get("expected_availability"), key_metrics.get("expected_availability", 0.0)),
            3,
        )
        key_metrics["annual_carbon_emission"] = round(
            _safe_float(environmental_metrics.get("annual_carbon_emission"), key_metrics.get("annual_carbon_emission", 0.0)),
            2,
        )
        if roi > 0:
            key_metrics["roi"] = roi
        if payback_period > 0:
            key_metrics["payback_period"] = payback_period
        normalized["key_metrics"] = key_metrics

        economic_section = dict(normalized.get("economic_section") or {})
        economic_content = dict(economic_section.get("content") or {})
        economic_content["total_cost"] = total_cost
        if roi > 0:
            economic_content["roi"] = roi
        if payback_period > 0:
            economic_content["payback_period"] = payback_period
        economic_section["content"] = economic_content
        normalized["economic_section"] = economic_section

        environmental_section = dict(normalized.get("environmental_section") or {})
        environmental_content = dict(environmental_section.get("content") or {})
        environmental_content["pue"] = key_metrics["pue"]
        environmental_content["green_power_ratio"] = key_metrics["green_power_ratio"]
        environmental_content["annual_carbon_emission"] = key_metrics["annual_carbon_emission"]
        environmental_section["content"] = environmental_content
        normalized["environmental_section"] = environmental_section

        power_section = dict(normalized.get("power_reliability_section") or {})
        power_content = dict(power_section.get("content") or {})
        power_content["tier_level"] = key_metrics["tier_level"]
        power_content["expected_availability"] = key_metrics["expected_availability"]
        power_section["content"] = power_content
        normalized["power_reliability_section"] = power_section

        return normalized

    def _parse_json_response(self, content: str) -> dict:
        """Parse JSON response."""
        import re

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        stack = []
        start_idx = None
        for i, char in enumerate(content):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}' and stack:
                stack.pop()
                if not stack and start_idx is not None:
                    try:
                        json_str = content[start_idx:i+1]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

        sys.stderr.write(f"[WARN] Failed to parse JSON, using default values\n")
        return {
            "name": "Construction Solution",
            "summary": "Synthesized expert opinions to generate solution",
            "overall_scores": {"overall": 0.75},
            "key_metrics": {},
            "economic_section": {},
            "power_reliability_section": {},
            "environmental_section": {},
            "trade_offs": [],
            "risks": [],
            "recommendations": [],
            "confidence": 0.6
        }

    def _on_stream_chunk(self, chunk: str):
        """Stream callback."""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class OutputNode:
    """Output node."""

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """Build the final output payload."""
        solution = state.get("solution", {})
        streaming_output = state.get("streaming_output", [])

        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Final Solution]\n")
        sys.stdout.write("="*60 + "\n")

        sys.stdout.write(f"\nSolution name: {solution.get('name', 'Unnamed')}\n")
        sys.stdout.write(f"Solution summary: {solution.get('summary', '')}\n")
        sys.stdout.write(f"\nOverall score: {solution.get('overall_scores', {}).get('overall', 0):.2f}\n")
        sys.stdout.flush()

        return {
            "current_step": "completed",
            "final_solution": solution,
            "streaming_output": streaming_output
        }




