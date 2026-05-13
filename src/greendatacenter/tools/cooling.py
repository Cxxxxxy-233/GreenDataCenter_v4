import os
import sys
import json
from typing import TypedDict, Any, Dict, Optional
from pydantic import BaseModel, Field

# 将项目的根目录添加到Python的模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入大模型相关库
from langchain.tools import tool

# ======================== 核心映射表 ========================
CITY_TO_PROVINCE = {
    "乌兰察布": "内蒙古", "北京": "北京", "上海": "上海", "广州": "广东",
    "深圳": "广东", "杭州": "浙江", "成都": "四川", "武汉": "湖北",
    "西安": "陕西", "南京": "江苏", "张家口": "河北", "三亚": "海南", "丽江": "云南"
}
# 温度对制冷能效系数（COP）的修正因子
TEMP_COP_CORRECTION = {
    "≤0": 1.2, "1-10": 1.1, "11-20": 1.0, "21-30": 0.9, ">30": 0.8
}
# 北方省份列表（用于余热回收系数的地域修正）
NORTHERN_PROVINCES = [
    "内蒙古", "北京", "天津", "河北", "山西", "辽宁", 
    "吉林", "黑龙江", "陕西", "甘肃", "青海", "宁夏", "新疆"
]
# 水资源紧缺综合评价指数 CWSI (Water Scarcity Index, 0~1，值越小越缺水)
CWSI_MAP = {
    "北京": 0.44, "天津": 0.38, "河北": 0.31, "上海": 0.61, "江苏": 0.54,
    "浙江": 0.64, "广东": 0.64, "四川": 0.51, "重庆": 0.51, "内蒙古": 0.39,
    "贵州": 0.46, "甘肃": 0.35, "宁夏": 0.31, "default": 0.50
}
# 各省份制冷基准参数（用于兜底规则）
PROVINCE_COOLING_BASE_PARAMS = {
    "北京": {"PUE_Limit": 1.15, "WUE_Limit": 1.6, "cabinet_power_limit": 20.0},
    "上海": {"PUE_Limit": 1.25, "WUE_Limit": 1.8, "cabinet_power_limit": 20.0},
    "广东": {"PUE_Limit": 1.25, "WUE_Limit": 1.8, "cabinet_power_limit": 20.0},
    "浙江": {"PUE_Limit": 1.25, "WUE_Limit": 1.8, "cabinet_power_limit": 20.0},
    "内蒙古": {"PUE_Limit": 1.15, "WUE_Limit": 1.5, "cabinet_power_limit": 25.0},
    "四川": {"PUE_Limit": 1.20, "WUE_Limit": 1.6, "cabinet_power_limit": 20.0},
    "default": {"PUE_Limit": 1.30, "WUE_Limit": 1.8, "cabinet_power_limit": 20.0}
}

# ======================== 成本与LCOE相关配置 ========================
# 制冷方案单位成本（元/kW）：初始投资成本
COOLING_COST_PER_KW = {
    # 房间级
    "传统房间级CRAC(下送风)+冷通道封闭": 800,
    "传统房间级CRAC(上送风)+热通道封闭": 850,
    "行间空调(行间CRAC)+冷热通道封闭": 900,
    "房间级CRAC+直接空气侧自然冷却(节能器)": 1000,
    "房间级CRAC+间接空气侧自然冷却(板式换热器)": 1200,
    "房间级CRAC+水侧自然冷却(冷却塔旁通)": 1100,
    "房间级CRAC+空气-水联合自然冷却": 1300,
    "集装箱式数据中心+直接新风自然冷却": 1500,
    "水蓄冷+房间级CRAC风冷系统": 1400,
    "相变材料(PCM)蓄冷+房间级CRAC风冷系统": 1600,
    # 机架级
    "机架级液冷后门+闭式冷却水系统": 2000,
    "冷板式液冷+开式冷却塔": 2500,
    "冷板式液冷+混合型干冷器": 2800,
    "冷板式液冷+水侧自然冷却(干冷器)": 2600,
    "冷板式液冷+吸收式制冷余热利用系统": 3500,
    "分离式热管系统+自然冷却": 2200,
    "集成式热虹吸+机械制冷双模式系统": 2400,
    "单相浸没式液冷+干冷器": 4000,
    "两相浸没式液冷+干冷器": 5000,
    "闭式循环喷雾冷却系统": 3800,
    "闭式循环射流冲击冷却系统": 4200,
    "喷雾-射流混合冷却系统": 4500,
    # 芯片级
    "歧管式微通道(MMC)直接液冷": 5500,
    "芯片-微流控共设计直接液冷": 7000,
    "嵌入式热管芯片级冷却": 3000,
    "微喷射阵列芯片级冷却": 5800,
}

# 运维成本系数（年运维成本/初始投资）
OP_COST_FACTOR = {
    "风冷类": 0.02,   # 房间级风冷为主
    "液冷类": 0.05,   # 机架/芯片级液冷为主
    "自然冷却类": 0.03, # 含自然冷却模块
}

# 折现率、使用年限（LCOE计算参数）
DISCOUNT_RATE = 0.08  # 年折现率
LIFESPAN_YEARS = 10   # 设备使用年限
ELECTRICITY_PRICE = 0.65  # 电价（元/kWh）


# ======================== 输入参数模型（Tool规范） ========================
class CoolingSchemeToolInput(BaseModel):
    """制冷方案生成Tool的输入参数模型"""
    user_requirements: Optional[Dict[str, Any]] = Field(
        default=None,
        description="用户需求参数，包含算力密度、PUE/WUE目标、绿电目标等",
    )
    environmental_data: Dict[str, Any] = Field(description="环境数据，包含年均温、地域等")
    energy_plan: Optional[Dict[str, Any]] = Field(default={}, description="绿电规划数据")

    location: Optional[str] = Field(default=None, description="数据中心所在城市")
    planned_load_kw: Optional[float] = Field(default=None, description="IT负荷（kW）")
    planned_load: Optional[float] = Field(default=None, description="IT负荷（kW）")
    computing_power_density: Optional[float] = Field(default=None, description="算力密度（kW/机柜）")
    pue_target: Optional[float] = Field(default=None, description="PUE目标值")
    wue_target: Optional[float] = Field(default=None, description="WUE目标值（L/kWh）")
    green_power_ratio: Optional[float] = Field(default=None, description="绿电消纳率（0-1）")
    green_energy_target: Optional[float] = Field(default=None, description="绿电消纳率目标（0-100）")
    priority: Optional[str] = Field(default=None, description="优先级（economic/green/reliable）")

# ======================== 核心制冷智能体类 ========================
class CoolingCalculator:
    def __init__(self):        
        pass

    def get_cop_correction_factor(self, annual_temp: float) -> float:
        """获取温度对应的COP修正因子"""
        if annual_temp <= 0:
            return TEMP_COP_CORRECTION["≤0"]
        elif 1 <= annual_temp <= 10:
            return TEMP_COP_CORRECTION["1-10"]
        elif 11 <= annual_temp <= 20:
            return TEMP_COP_CORRECTION["11-20"]
        elif 21 <= annual_temp <= 30:
            return TEMP_COP_CORRECTION["21-30"]
        else:
            return TEMP_COP_CORRECTION[">30"]

    def _calculate_recovery_coeff(self, user_reqs: Dict[str, Any], province: str) -> float:
        """计算余热回收系数"""
        cab_power = user_reqs.get('computing_power_density', 8)
        cab_power_limit = user_reqs.get("cabinet_power_limit", 20.0)
        green_energy_target = user_reqs.get("green_energy_target", 90)
        if green_energy_target <= 1:
            green_energy_target = green_energy_target * 100
        is_liquid_cooling = cab_power > 20 or cab_power >= cab_power_limit
        base_coeff = 0.75 if is_liquid_cooling else 0.55
        region_correction = 0.1 if province in NORTHERN_PROVINCES else 0.0
        green_correction = 0.05 if green_energy_target >= 90 else -0.05
        density_correction = 0.05 if cab_power > 60 else (-0.05 if cab_power <= 20 else 0.0)
        return round(min(0.8, max(0.0, base_coeff + region_correction + green_correction + density_correction)), 2)

    def evaluate_cooling_strategies(self, project_info: Dict[str, Any], province: str) -> Dict[str, Any]:
        """评估所有制冷策略，输出最优策略+寻优轨迹"""
        cabinet_power = project_info.get("computing_power_density", 8.0)
        priority = project_info.get("priority", "环保型")
        
        # 优先级映射
        priority_mapping = {
            "reliable": "可靠型",
            "economic": "经济型",
            "green": "环保型"
        }
        if isinstance(priority, str) and "," in priority:
            priority_list = priority.split(",")
            for p in priority_list:
                p = p.strip()
                if p in priority_mapping:
                    priority = priority_mapping[p]
                    break
        elif priority in priority_mapping:
            priority = priority_mapping[priority]
        
        cwsi = CWSI_MAP.get(province, CWSI_MAP["default"])
        # 动态权重计算
        alpha, beta, gamma, delta, epsilon = 0.3, 0.2, 0.3, 0.1, 0.1
        if cwsi <= 0.45:
            beta += 0.3
        elif cwsi >= 0.6:
            beta -= 0.1
        if priority == "环保型":
            delta += 0.2
            epsilon += 0.1
            gamma -= 0.1
        elif priority == "经济型":
            gamma += 0.3
            delta -= 0.1
        elif priority == "可靠型":
            alpha += 0.25
            gamma -= 0.15
            epsilon += 0.15
        total_weight = alpha + beta + gamma + delta + epsilon
        w = {
            "alpha": round(alpha/total_weight, 2), 
            "beta": round(beta/total_weight, 2), 
            "gamma": round(gamma/total_weight, 2), 
            "delta": round(delta/total_weight, 2), 
            "epsilon": round(epsilon/total_weight, 2)
        }

        # 全量制冷策略库
        strategies = [
            # 一、房间级制冷策略(≤30kW/机架)
            {"name": "传统房间级CRAC(下送风)+冷通道封闭", "max_kw": 15, "f_pue": 1.45, "f_wue": 0.10, "f_tco": 0.60, "f_cue": 1.40, "f_whr": 0.20},
            {"name": "传统房间级CRAC(上送风)+热通道封闭", "max_kw": 18, "f_pue": 1.23, "f_wue": 0.10, "f_tco": 0.65, "f_cue": 1.20, "f_whr": 0.25},
            {"name": "行间空调(行间CRAC)+冷热通道封闭", "max_kw": 20, "f_pue": 1.35, "f_wue": 0.10, "f_tco": 0.70, "f_cue": 1.30, "f_whr": 0.30},
            {"name": "房间级CRAC+直接空气侧自然冷却(节能器)", "max_kw": 15, "f_pue": 1.30, "f_wue": 0.05, "f_tco": 0.75, "f_cue": 1.25, "f_whr": 0.25},
            {"name": "房间级CRAC+间接空气侧自然冷却(板式换热器)", "max_kw": 20, "f_pue": 1.22, "f_wue": 0.05, "f_tco": 0.85, "f_cue": 1.18, "f_whr": 0.35},
            {"name": "房间级CRAC+水侧自然冷却(冷却塔旁通)", "max_kw": 20, "f_pue": 1.25, "f_wue": 0.80, "f_tco": 0.80, "f_cue": 1.20, "f_whr": 0.40},
            {"name": "房间级CRAC+空气-水联合自然冷却", "max_kw": 22, "f_pue": 1.15, "f_wue": 0.50, "f_tco": 0.90, "f_cue": 1.12, "f_whr": 0.40},
            {"name": "集装箱式数据中心+直接新风自然冷却", "max_kw": 8, "f_pue": 1.32, "f_wue": 0.05, "f_tco": 0.70, "f_cue": 1.26, "f_whr": 0.25},
            {"name": "水蓄冷+房间级CRAC风冷系统", "max_kw": 15, "f_pue": 1.36, "f_wue": 0.20, "f_tco": 0.85, "f_cue": 1.27, "f_whr": 0.22},
            {"name": "相变材料(PCM)蓄冷+房间级CRAC风冷系统", "max_kw": 10, "f_pue": 1.38, "f_wue": 0.05, "f_tco": 0.80, "f_cue": 1.28, "f_whr": 0.20},
            # 二、机架级制冷策略(30-1000kW/机架)
            {"name": "机架级液冷后门+闭式冷却水系统", "max_kw": 30, "f_pue": 1.20, "f_wue": 0.60, "f_tco": 0.95, "f_cue": 1.15, "f_whr": 0.60},
            {"name": "冷板式液冷+开式冷却塔", "max_kw": 60, "f_pue": 1.15, "f_wue": 2.10, "f_tco": 1.00, "f_cue": 1.10, "f_whr": 0.75},
            {"name": "冷板式液冷+混合型干冷器", "max_kw": 60, "f_pue": 1.20, "f_wue": 0.50, "f_tco": 1.30, "f_cue": 1.15, "f_whr": 0.75},
            {"name": "冷板式液冷+水侧自然冷却(干冷器)", "max_kw": 60, "f_pue": 1.12, "f_wue": 0.80, "f_tco": 1.10, "f_cue": 1.08, "f_whr": 0.78},
            {"name": "冷板式液冷+吸收式制冷余热利用系统", "max_kw": 60, "f_pue": 1.10, "f_wue": 2.00, "f_tco": 1.60, "f_cue": 1.03, "f_whr": 0.88},
            {"name": "分离式热管系统+自然冷却", "max_kw": 30, "f_pue": 1.18, "f_wue": 0.05, "f_tco": 1.05, "f_cue": 1.07, "f_whr": 0.70},
            {"name": "集成式热虹吸+机械制冷双模式系统", "max_kw": 40, "f_pue": 1.16, "f_wue": 0.40, "f_tco": 1.20, "f_cue": 1.06, "f_whr": 0.72},
            {"name": "单相浸没式液冷+干冷器", "max_kw": 200, "f_pue": 1.08, "f_wue": 0.10, "f_tco": 1.90, "f_cue": 1.05, "f_whr": 0.85},
            {"name": "两相浸没式液冷+干冷器", "max_kw": 999, "f_pue": 1.05, "f_wue": 0.05, "f_tco": 2.20, "f_cue": 1.02, "f_whr": 0.90},
            {"name": "闭式循环喷雾冷却系统", "max_kw": 150, "f_pue": 1.12, "f_wue": 0.30, "f_tco": 1.70, "f_cue": 1.07, "f_whr": 0.80},
            {"name": "闭式循环射流冲击冷却系统", "max_kw": 200, "f_pue": 1.10, "f_wue": 0.25, "f_tco": 1.80, "f_cue": 1.06, "f_whr": 0.82},
            {"name": "喷雾-射流混合冷却系统", "max_kw": 250, "f_pue": 1.09, "f_wue": 0.28, "f_tco": 2.00, "f_cue": 1.05, "f_whr": 0.83},
            # 三、芯片级制冷策略(>250kW/机架)
            {"name": "歧管式微通道(MMC)直接液冷", "max_kw": 500, "f_pue": 1.06, "f_wue": 0.15, "f_tco": 2.30, "f_cue": 1.04, "f_whr": 0.87},
            {"name": "芯片-微流控共设计直接液冷", "max_kw": 800, "f_pue": 1.03, "f_wue": 0.10, "f_tco": 2.80, "f_cue": 1.01, "f_whr": 0.92},
            {"name": "嵌入式热管芯片级冷却", "max_kw": 150, "f_pue": 1.15, "f_wue": 0.05, "f_tco": 1.50, "f_cue": 1.12, "f_whr": 0.75},
            {"name": "微喷射阵列芯片级冷却", "max_kw": 300, "f_pue": 1.07, "f_wue": 0.12, "f_tco": 2.50, "f_cue": 1.03, "f_whr": 0.86},
        ]

        # 策略寻优
        best_strategy = None
        min_score = float('inf')
        trace_log = f"【寻优环境】算力密度={cabinet_power}kW, 偏好={priority}, 水资源CWSI={cwsi}\n"
        trace_log += f"【动态权重】α(PUE)={w['alpha']}, β(WUE)={w['beta']}, γ(TCO)={w['gamma']}, δ(CUE)={w['delta']}, ε(WHR)={w['epsilon']}\n"
        trace_log += "【方案打分】计算公式: F = α·f(PUE) + β·f(WUE) + γ·f(TCO) + δ·f(CUE) - ε·f(WHR)\n"
        
        # 存储所有可行方案的得分（用于前端排序与展示）
        strategy_scores = []
        rejected_strategies = []
        for s in strategies:
            if cabinet_power > s["max_kw"]:
                trace_log += f" - 方案 [{s['name']}] 被一票否决：无法满足 {cabinet_power}kW 物理散热极限。\n"
                rejected_strategies.append(s["name"])
                continue
            score = (w["alpha"] * s["f_pue"] + w["beta"] * s["f_wue"] + w["gamma"] * s["f_tco"] + w["delta"] * s["f_cue"] - w["epsilon"] * s["f_whr"])
            trace_log += f" - 方案 [{s['name']}] 得分: {score:.3f} (PUE代价:{s['f_pue']}, WUE代价:{s['f_wue']}, TCO代价:{s['f_tco']})\n"
            strategy_scores.append({
                "strategy": s["name"],
                "name": s["name"],
                "total_score": round(score, 4),
                "score": round(score, 4),
                "max_kw": s["max_kw"],
                "pue": s["f_pue"],
                "wue": s["f_wue"],
                "tco": s["f_tco"],
                "cue": s["f_cue"],
                "whr": s["f_whr"],
                "f_pue": s["f_pue"],
                "f_wue": s["f_wue"],
                "f_tco": s["f_tco"],
                "f_cue": s["f_cue"],
                "f_whr": s["f_whr"],
            })
            if score < min_score:
                min_score = score
                best_strategy = s

        if not best_strategy:
            raise ValueError("未找到满足当前算力密度约束的可行制冷策略")

        strategy_scores = sorted(strategy_scores, key=lambda item: item["total_score"])
        for index, item in enumerate(strategy_scores, start=1):
            item["ranking"] = index

        trace_log += f"★ 【最终决策】代价最小路线为：[{best_strategy['name']}]，最终得分：{min_score:.3f}\n"

        objective_weights = {
            "PUE": w["alpha"],
            "WUE": w["beta"],
            "TCO": w["gamma"],
            "CUE": w["delta"],
            "WHR": w["epsilon"],
        }

        return {
            "best_strategy_name": best_strategy["name"], 
            "optimization_trace": trace_log,
            "objective_weights": objective_weights,
            "optimization_summary": {
                "selected_strategy": best_strategy["name"],
                "selected_score": round(min_score, 4),
                "objective_weights": objective_weights,
                "priority_mode": priority,
                "water_scarcity_index": cwsi,
                "feasible_strategy_count": len(strategy_scores),
                "rejected_strategy_count": len(rejected_strategies),
            },
            "all_strategy_scores": strategy_scores  # 所有可行方案得分（用于LCOE排序）
        }

    def extract_cooling_params(self, user_reqs: Dict[str, Any], best_strategy_name: str) -> Dict[str, float]:
        """提取制冷核心参数"""
        cab_power_limit = user_reqs.get("cabinet_power_limit", 20.0)
        pue_limit_input = user_reqs.get("pue_limit", 1.30)
        wue_limit_input = user_reqs.get("wue_limit", 1.60)
        agent_recovery_coeff = self._calculate_recovery_coeff(user_reqs, user_reqs.get("location", "默认"))
        is_liquid = "液冷" in best_strategy_name

        return {
            "PUE_Limit": pue_limit_input, 
            "WUE_Limit": wue_limit_input,
            "cooling_eff_coeff": 4.5 if is_liquid else 3.8, 
            "waste_heat_recovery_coeff": agent_recovery_coeff,
            "facility_loss_coeff": 0.07, 
            "cabinet_power_limit": cab_power_limit,
            "regional_cooling_preference": best_strategy_name
        }

    def calculate_cooling_kpis(self, params: Dict[str, Any], project_info: Dict[str, Any], env_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算制冷关键性能指标"""
        it_load = project_info.get("planned_load", 0)
        cabinet_power = project_info.get("computing_power_density", 0)
        annual_temp = env_data.get("annual_temperature", 15.0)
        province = project_info.get("location", "默认")
        cwsi = CWSI_MAP.get(province, CWSI_MAP["default"])
        
        cooling_tech = params.get("regional_cooling_preference", "风冷")
        density_correction = 1.1 if cabinet_power >= params.get("cabinet_power_limit", 20.0) else 1.0
        cop_correction = self.get_cop_correction_factor(annual_temp)
        corrected_cop = params.get("cooling_eff_coeff", 4.0) * cop_correction
        cooling_load_kw = it_load * 1.1 * density_correction
        waste_heat_recovery_kw = cooling_load_kw * params.get("waste_heat_recovery_coeff", 0.0)
        corrected_cooling_load = max(0.0, cooling_load_kw - waste_heat_recovery_kw)
        
        cooling_power_kw = corrected_cooling_load / corrected_cop if corrected_cop > 0 else 0.0
        facility_loss_kw = it_load * params.get("facility_loss_coeff", 0.1)
        total_energy = it_load + cooling_power_kw + facility_loss_kw
        pue = total_energy / it_load if it_load > 0 else 1.0
        
        wue = self._calculate_wue(cooling_tech, cwsi, annual_temp, cooling_load_kw, it_load)
        return {
            "predicted_PUE": round(pue, 3), 
            "predicted_WUE": round(wue, 3),
            "waste_heat_recovery_kw": round(waste_heat_recovery_kw, 2),
            "cooling_power_kw": round(cooling_power_kw, 2),
            "facility_loss_kw": round(facility_loss_kw, 2), 
            "corrected_cop": round(corrected_cop, 2),
            "cooling_load_kw": round(cooling_load_kw, 2)  # 新增：制冷负荷（用于成本计算）
        }
    
    def _calculate_wue(self, cooling_tech: str, cwsi: float, annual_temp: float, cooling_load_kw: float, it_load_kw: float) -> float:
        """计算WUE（水使用效率）"""
        base_wue = 1.8
        if "液冷" in cooling_tech:
            base_wue = 0.8
        elif "干冷" in cooling_tech or "风冷" in cooling_tech:
            base_wue = 0.3
        elif "冷却塔" in cooling_tech or "水冷" in cooling_tech:
            base_wue = 1.8
        
        cwsi_factor = 1.0 + (cwsi - 0.5) * 0.5
        if cwsi <= 0.45:
            cwsi_factor = 0.7
        elif cwsi >= 0.6:
            cwsi_factor = 1.3
        
        temp_factor = 1.0
        if annual_temp > 25:
            temp_factor = 1.2
        elif annual_temp < 10:
            temp_factor = 0.85
        
        load_factor = min(1.0, cooling_load_kw / (it_load_kw * 1.2)) if it_load_kw > 0 else 1.0
        predicted_wue = base_wue * cwsi_factor * temp_factor * load_factor
        return max(0.1, min(3.0, predicted_wue))

    def calculate_economic_indicators(self, strategy_name: str, cooling_load_kw: float, predicted_pue: float, it_load_kw: float) -> Dict[str, float]:
        """
        计算经济指标：LCOE、初始投资、年运维成本
        :param strategy_name: 制冷方案名称
        :param cooling_load_kw: 制冷负荷（kW）
        :param predicted_pue: 预测PUE
        :param it_load_kw: IT负荷（kW）
        :return: 经济指标字典
        """
        # 1. 初始投资（万元）
        unit_cost = COOLING_COST_PER_KW.get(strategy_name, 1000)  # 元/kW
        initial_investment = (cooling_load_kw * unit_cost) / 10000  # 转换为万元
        
        # 2. 年运维成本（万元）
        if "液冷" in strategy_name:
            op_factor = OP_COST_FACTOR["液冷类"]
        elif "自然冷却" in strategy_name:
            op_factor = OP_COST_FACTOR["自然冷却类"]
        else:
            op_factor = OP_COST_FACTOR["风冷类"]
        annual_op_cost = initial_investment * op_factor
        
        # 3. 年能耗（kWh）：基于PUE和IT负荷
        annual_operating_hours = 8760  # 年运行小时数
        total_energy_consumption = it_load_kw * annual_operating_hours * predicted_pue
        cooling_energy_consumption = total_energy_consumption - (it_load_kw * annual_operating_hours)
        
        # 4. 年电费成本（万元）
        annual_electricity_cost = (cooling_energy_consumption * ELECTRICITY_PRICE) / 10000
        
        # 5. LCOE计算（平准化度电成本，元/kWh）
        # 公式：LCOE = (初始投资*年金系数 + 年运维成本 + 年电费) / 年发电量
        annuity_factor = DISCOUNT_RATE * (1 + DISCOUNT_RATE)**LIFESPAN_YEARS / ((1 + DISCOUNT_RATE)**LIFESPAN_YEARS - 1)
        annual_capital_cost = initial_investment * annuity_factor * 10000  # 转换为元
        total_annual_cost = annual_capital_cost + (annual_op_cost * 10000) + (annual_electricity_cost * 10000)
        lcoe = total_annual_cost / (it_load_kw * annual_operating_hours)
        
        return {
            "initial_investment": round(initial_investment, 2),  # 初始投资（万元）
            "annual_op_cost": round(annual_op_cost, 2),          # 年运维成本（万元）
            "annual_electricity_cost": round(annual_electricity_cost, 2),  # 年电费（万元）
            "lcoe": round(lcoe, 4)                               # LCOE（元/kWh）
        }

    def run(self, user_requirements: Dict[str, Any], environmental_data: Dict[str, Any], energy_plan: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        核心执行函数：生成制冷方案+经济分析
        :param user_requirements: 用户需求
        :param environmental_data: 环境数据
        :param energy_plan: 绿电规划
        :return: 完整制冷方案结果
        """
        # 1. 数据预处理
        normalized = _normalize_user_requirements(user_requirements)
        project_info = {
            **normalized,
            "cabinet_power_limit": normalized.get("cabinet_power_limit", 20.0),
            "pue_limit": normalized.get("pue_target", 1.30),
            "wue_limit": normalized.get("wue_target", 1.60),
        }
        region = project_info.get("location", "北京")
        province = CITY_TO_PROVINCE.get(region, "北京")
        annual_temp = environmental_data.get("annual_temperature", 15.0)
        cabinet_power = project_info.get("computing_power_density", 8.0)
        it_load_kw = project_info.get("planned_load", 0)

        # 2. 策略寻优
        opt_result = self.evaluate_cooling_strategies(project_info, province)
        
        # 4. 参数提取
        extracted_params = self.extract_cooling_params(project_info, opt_result["best_strategy_name"])
        
        # 5. KPI计算
        kpis = self.calculate_cooling_kpis(extracted_params, project_info, environmental_data)
        
        # 6. 经济指标计算
        economic_indicators = self.calculate_economic_indicators(
            strategy_name=opt_result["best_strategy_name"],
            cooling_load_kw=kpis["cooling_load_kw"],
            predicted_pue=kpis["predicted_PUE"],
            it_load_kw=it_load_kw
        )
        
        # 8. 结果整合
        cooling_plan = {
            "cooling_technology": extracted_params.get("regional_cooling_preference", "未知"),
            "estimated_pue": kpis.get("predicted_PUE", 1.3),
            "predicted_wue": kpis.get("predicted_WUE", 1.6),
            "cooling_power_consumption": kpis.get("cooling_power_kw", 0),
            "waste_heat_recovery_kw": kpis.get("waste_heat_recovery_kw", 0),
            "strategy_optimization_trace": opt_result["optimization_trace"],
            "optimization_summary": opt_result.get("optimization_summary", {}),
            "objective_weights": opt_result.get("objective_weights", {}),
            "selected_strategy_name": opt_result.get("best_strategy_name"),
            "all_strategy_scores": opt_result.get("all_strategy_scores", []),
            "cooling_project_info": {
                "location": project_info.get("location", "未知"),
                "it_load_kW": project_info.get("planned_load", 0),
                "cabinet_power_kW": project_info.get("computing_power_density", 8),
                "target_pue": project_info.get("pue_target", 1.2),
                "green_energy_target": project_info.get("green_energy_target", 90)
            },
            "cooling_calc_params": {
                "PUE_Limit": extracted_params.get("PUE_Limit", 1.30),
                "WUE_Limit": extracted_params.get("WUE_Limit", 1.60),
                "cooling_eff_coeff": extracted_params.get("cooling_eff_coeff", 4.0),
                "facility_loss_coeff": extracted_params.get("facility_loss_coeff", 0.07),
                "regional_cooling_preference": extracted_params.get("regional_cooling_preference", "未知")
            },
            "cooling_kpis": {
                "predicted_PUE": kpis.get("predicted_PUE", 1.3),
                "predicted_WUE": kpis.get("predicted_WUE", 1.6),
                "cooling_power_kw": kpis.get("cooling_power_kw", 0),
                "corrected_cop": kpis.get("corrected_cop", 4.0),
                "waste_heat_recovery_kw": kpis.get("waste_heat_recovery_kw", 0),
                "cooling_load_kw": kpis.get("cooling_load_kw", 0)
            },
            "economic_indicators": economic_indicators,  # 新增：经济指标
            "waste_heat_recovery_strategy": f"基于{project_info.get('location', '本地')}地区的气候条件，推荐采用{'液冷余热回收系统' if kpis.get('waste_heat_recovery_kw', 0) > 0 else '传统风冷系统'}。预计可回收{kpis.get('waste_heat_recovery_kw', 0):.1f} kW余热，可用于园区供暖或预热新风系统。"
        }
        
        return cooling_plan

# ======================== Tool 封装 ========================
@tool("cooling-scheme-generator", args_schema=CoolingSchemeToolInput, return_direct=True)
def cooling_scheme_generator_tool(
    environmental_data: Dict[str, Any],
    user_requirements: Optional[Dict[str, Any]] = None,
    energy_plan: Optional[Dict[str, Any]] = None,
    location: Optional[str] = None,
    planned_load_kw: Optional[float] = None,
    planned_load: Optional[float] = None,
    computing_power_density: Optional[float] = None,
    pue_target: Optional[float] = None,
    wue_target: Optional[float] = None,
    green_power_ratio: Optional[float] = None,
    green_energy_target: Optional[float] = None,
    priority: Optional[str] = None,
) -> Dict[str, Any]:
    """
    数据中心制冷方案生成Tool
    输入用户需求、环境数据、绿电规划，输出包含经济分析的完整制冷方案
    
    Args:
        user_requirements: 用户需求参数，包含以下关键字段：
            - computing_power_density: 单机柜算力密度（kW）
            - planned_load: IT总负荷（kW）
            - pue_target: PUE目标值
            - wue_target: WUE目标值（L/kWh）
            - green_energy_target: 绿电消纳目标（%）
            - location: 项目所在地（城市）
            - priority: 优先级（economic/green/reliable）
        environmental_data: 环境数据，包含：
            - annual_temperature: 年均温度（℃）
        可选的显式调参字段：
            - pue_target / wue_target / priority / computing_power_density 等

    调参说明：
        - pue_target / wue_target: 目标值越严格，倾向选择能效更高的方案
        - computing_power_density: 影响可行策略范围（超出 max_kw 的方案会被排除）
        - priority: 影响权重分配（economic/green/reliable）
        - green_power_ratio / green_energy_target: 影响余热回收系数修正
    
    Returns:
        制冷方案字典，包含：
            - cooling_technology: 推荐制冷技术
            - estimated_pue: 预测PUE
            - predicted_wue: 预测WUE
            - economic_indicators: 经济指标（LCOE、初始投资、运维成本等）
            - scheme_detail_brief: 完整方案报告
            - 其他核心参数与KPI
    """
    payload = {
        "user_requirements": user_requirements,
        "environmental_data": environmental_data,
        "energy_plan": energy_plan or {},
        "location": location,
        "planned_load_kw": planned_load_kw,
        "planned_load": planned_load,
        "computing_power_density": computing_power_density,
        "pue_target": pue_target,
        "wue_target": wue_target,
        "green_power_ratio": green_power_ratio,
        "green_energy_target": green_energy_target,
        "priority": priority,
    }
    merged_requirements = _build_user_requirements_from_input(payload)
    calculator = CoolingCalculator()
    return calculator.run(merged_requirements, environmental_data, energy_plan or {})


def compute_cooling_plan(
    user_requirements: Dict[str, Any],
    environmental_data: Dict[str, Any],
    energy_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """非LLM路径的制冷方案计算入口。"""
    calculator = CoolingCalculator()
    return calculator.run(user_requirements, environmental_data, energy_plan or {})


def _build_user_requirements_from_input(data: Dict[str, Any]) -> Dict[str, Any]:
    base = dict(data.get("user_requirements") or {})
    overrides = {
        "location": data.get("location"),
        "planned_load_kw": data.get("planned_load_kw"),
        "planned_load": data.get("planned_load"),
        "computing_power_density": data.get("computing_power_density"),
        "pue_target": data.get("pue_target"),
        "wue_target": data.get("wue_target"),
        "green_power_ratio": data.get("green_power_ratio"),
        "green_energy_target": data.get("green_energy_target"),
        "priority": data.get("priority"),
    }
    for key, value in overrides.items():
        if value is not None:
            base[key] = value
    return base


def _normalize_user_requirements(user_requirements: Dict[str, Any]) -> Dict[str, Any]:
    planned_load_kw = user_requirements.get("planned_load")
    if planned_load_kw is None:
        planned_load_kw = user_requirements.get("planned_load_kw")
    if planned_load_kw is None:
        planned_load_kw = user_requirements.get("total_power")

    green_target = user_requirements.get("green_energy_target")
    if green_target is None:
        green_target = user_requirements.get("green_power_ratio")
    if green_target is None:
        green_target = 90
    if green_target <= 1:
        green_target = green_target * 100

    return {
        **user_requirements,
        "planned_load": planned_load_kw or 0,
        "green_energy_target": green_target,
    }

# ======================== 测试代码 ========================
if __name__ == "__main__":
    test_cases = [
        {
            "name": "北方高密度-环保优先",
            "user_requirements": {
                "computing_power_density": 30,
                "planned_load": 1000,
                "pue_target": 1.18,
                "wue_target": 0.8,
                "green_energy_target": 95,
                "location": "乌兰察布",
                "priority": "green",
            },
            "environmental_data": {"annual_temperature": 5.0},
            "energy_plan": {
                "estimated_green_ratio": 95,
                "pv_capacity": 500,
                "ppa_ratio": 30,
            },
        },
        {
            "name": "南方中密度-经济优先",
            "user_requirements": {
                "computing_power_density": 18,
                "planned_load_kw": 600,
                "pue_target": 1.25,
                "wue_target": 1.2,
                "green_power_ratio": 0.6,
                "location": "深圳",
                "priority": "economic",
            },
            "environmental_data": {"annual_temperature": 26.0},
            "energy_plan": {},
        },
    ]

    for case in test_cases:
        result = cooling_scheme_generator_tool.invoke({
            "user_requirements": case["user_requirements"],
            "environmental_data": case["environmental_data"],
            "energy_plan": case.get("energy_plan", {}),
        })

        print("\n=== 测试用例 ===")
        print(f"名称：{case['name']}")
        print(f"推荐技术：{result['cooling_technology']}")
        print(f"预测PUE：{result['estimated_pue']}")
        print(f"预测WUE：{result['predicted_wue']}")
        print("\n--- 关键KPI ---")
        for key, value in result["cooling_kpis"].items():
            print(f"{key}: {value}")
        print("\n--- 经济指标 ---")
        for key, value in result["economic_indicators"].items():
            print(f"{key}: {value}")

