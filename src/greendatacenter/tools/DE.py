from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from scipy.optimize import NonlinearConstraint, differential_evolution
import warnings

TOOLS_DIR = Path(__file__).resolve().parent
CSV_DIR = TOOLS_DIR / "csv"
OUTPUT_DIR = TOOLS_DIR.parent / "output"
DEFAULT_LOAD_CSV_PATH = CSV_DIR / "Load.csv"
DEFAULT_WIND_CSV_PATH = CSV_DIR / "Wind.csv"
DEFAULT_PV_CSV_PATH = CSV_DIR / "PV.csv"

DEFAULT_SIM_HOURS = 160
DEFAULT_STORAGE_INITIAL_SOC_RATIO = 0.5
DEFAULT_MAX_CHARGE_RATE_RATIO = 0.6
DEFAULT_MAX_DISCHARGE_RATE_RATIO = 0.8
DEFAULT_CHARGE_EFF = 0.95
DEFAULT_DISCHARGE_EFF = 0.92
DEFAULT_SOC_MIN_RATIO = 0.2
DEFAULT_SOC_MAX_RATIO = 0.8


def _configure_matplotlib_font() -> None:
    """Prefer a usable Chinese font when available."""
    candidate_fonts = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "WenQuanYi Micro Hei",
    ]
    installed = {font.name for font in font_manager.fontManager.ttflist}

    selected_font = next((font for font in candidate_fonts if font in installed), None)
    if selected_font is not None:
        plt.rcParams["font.sans-serif"] = [selected_font, "DejaVu Sans"]
    else:
        plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]

    plt.rcParams["axes.unicode_minus"] = False
    warnings.filterwarnings(
        "ignore",
        message=r"Glyph .* missing from font\(s\)",
        category=UserWarning,
    )


_configure_matplotlib_font()


def _read_series(file_path: str | Path) -> np.ndarray:
    """Read a single-column numeric CSV series."""
    csv_path = Path(file_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    dataframe = pd.read_csv(csv_path, header=None, encoding="utf-8-sig")
    series = pd.to_numeric(dataframe.iloc[:, 0], errors="coerce").dropna().to_numpy(dtype=float)
    if series.size == 0:
        raise ValueError(f"No valid numeric data found in {csv_path}")
    return np.array(series, copy=True)


def _clip_non_negative(series: np.ndarray) -> np.ndarray:
    numeric_series = np.array(series, dtype=float, copy=True)
    numeric_series[numeric_series < 0] = 0.0
    return numeric_series


def _resolve_sim_hours(sim_hours: Optional[int], *series_lengths: int) -> int:
    available_length = min(series_lengths)
    if available_length <= 0:
        raise ValueError("No valid time-series data available for optimization")

    if sim_hours is None:
        return min(DEFAULT_SIM_HOURS, available_length)
    if sim_hours <= 0:
        raise ValueError("sim_hours must be > 0")
    if sim_hours > available_length:
        raise ValueError(f"sim_hours={sim_hours} exceeds available data length {available_length}")
    return sim_hours


def _resolve_load_series(
    data_center_load_mw: float,
    sim_hours: int,
    load_coeff_series: Optional[np.ndarray] = None,
    load_series_input: Optional[np.ndarray] = None,
    load_csv_path: Optional[str | Path] = None,
) -> np.ndarray:
    """Resolve the load profile used by the optimizer."""
    if load_series_input is not None:
        load_series = _clip_non_negative(np.array(load_series_input, dtype=float, copy=True))
        if len(load_series) < sim_hours:
            raise ValueError("load_series_input length is shorter than sim_hours")
        return load_series[:sim_hours]

    if load_coeff_series is not None:
        coefficients = _clip_non_negative(np.array(load_coeff_series, dtype=float, copy=True))
        if len(coefficients) < sim_hours:
            raise ValueError("load_coeff_series length is shorter than sim_hours")
        return data_center_load_mw * coefficients[:sim_hours]

    if load_csv_path is not None:
        coefficients = _clip_non_negative(_read_series(load_csv_path))
        if len(coefficients) < sim_hours:
            raise ValueError(f"Load profile in {load_csv_path} is shorter than sim_hours")
        return data_center_load_mw * coefficients[:sim_hours]

    return np.full(sim_hours, float(data_center_load_mw), dtype=float)


def _resolve_generation_series(
    sim_hours: int,
    series_input: Optional[np.ndarray],
    csv_path: Optional[str | Path],
    series_name: str,
) -> np.ndarray:
    if series_input is not None:
        series = _clip_non_negative(np.array(series_input, dtype=float, copy=True))
    elif csv_path is not None:
        series = _clip_non_negative(_read_series(csv_path))
    else:
        raise ValueError(f"{series_name} profile is required")

    if len(series) < sim_hours:
        raise ValueError(f"{series_name} profile length is shorter than sim_hours")
    return series[:sim_hours]


def update_system(
    state: Dict[str, float],
    load_val: float,
    wind_pu: float,
    pv_pu: float,
    wind_capacity_mw: float,
    pv_capacity_mw: float,
    storage_capacity_mwh: float,
    soc_min_ratio: float,
    soc_max_ratio: float,
    max_charge_rate_ratio: float,
    max_discharge_rate_ratio: float,
    charge_eff: float,
    discharge_eff: float,
) -> Dict[str, float]:
    """Update system state for a single hour."""
    soc_min = soc_min_ratio * storage_capacity_mwh
    soc_max = soc_max_ratio * storage_capacity_mwh
    max_charge_rate = max_charge_rate_ratio * storage_capacity_mwh
    max_discharge_rate = max_discharge_rate_ratio * storage_capacity_mwh

    wind_gen = max(0.0, wind_pu) * wind_capacity_mw
    pv_gen = max(0.0, pv_pu) * pv_capacity_mw
    renewable_total = wind_gen + pv_gen

    renewable_to_load = min(load_val, renewable_total)
    load_remaining = load_val - renewable_to_load
    renewable_surplus = renewable_total - renewable_to_load

    wind_to_load = 0.0
    pv_to_load = 0.0
    if renewable_total > 1e-12:
        wind_to_load = renewable_to_load * (wind_gen / renewable_total)
        pv_to_load = renewable_to_load * (pv_gen / renewable_total)

    stored_energy = 0.0
    renewable_to_storage_input = 0.0
    wind_to_storage_input = 0.0
    pv_to_storage_input = 0.0
    if renewable_surplus > 0.0 and state["storage_soc"] < soc_max:
        stored_energy = min(
            renewable_surplus * charge_eff,
            max_charge_rate,
            soc_max - state["storage_soc"],
        )
        renewable_to_storage_input = stored_energy / charge_eff if charge_eff > 0 else 0.0
        state["storage_soc"] += stored_energy

        if renewable_total > 1e-12:
            wind_share = wind_gen / renewable_total
            pv_share = pv_gen / renewable_total
            wind_to_storage_input = renewable_to_storage_input * wind_share
            pv_to_storage_input = renewable_to_storage_input * pv_share

    storage_discharge_draw = 0.0
    storage_to_load = 0.0
    if load_remaining > 0.0 and state["storage_soc"] > soc_min:
        storage_discharge_draw = min(
            load_remaining / discharge_eff,
            max_discharge_rate,
            state["storage_soc"] - soc_min,
        )
        storage_to_load = storage_discharge_draw * discharge_eff
        state["storage_soc"] -= storage_discharge_draw
        load_remaining -= storage_to_load

    grid_purchase = max(0.0, load_remaining)
    curtailed_energy = max(0.0, renewable_surplus - renewable_to_storage_input)
    state["storage_soc"] = float(np.clip(state["storage_soc"], soc_min, soc_max))

    state.update(
        {
            "load": load_val,
            "wind_generation": wind_gen,
            "pv_generation": pv_gen,
            "wind_to_load": wind_to_load,
            "pv_to_load": pv_to_load,
            "wind_to_storage_input": wind_to_storage_input,
            "pv_to_storage_input": pv_to_storage_input,
            "storage_charging": stored_energy,
            "storage_discharging": storage_to_load,
            "grid_purchase": grid_purchase,
            "curtailment": curtailed_energy,
            "loss_of_load": False,
            "unserved": 0.0,
        }
    )
    return state


def simulate_system(
    wind_capacity_mw: float,
    pv_capacity_mw: float,
    storage_capacity_mwh: float,
    load_series: np.ndarray,
    wind_pu_series: np.ndarray,
    pv_pu_series: np.ndarray,
    storage_initial_soc_ratio: float = DEFAULT_STORAGE_INITIAL_SOC_RATIO,
    soc_min_ratio: float = DEFAULT_SOC_MIN_RATIO,
    soc_max_ratio: float = DEFAULT_SOC_MAX_RATIO,
    max_charge_rate_ratio: float = DEFAULT_MAX_CHARGE_RATE_RATIO,
    max_discharge_rate_ratio: float = DEFAULT_MAX_DISCHARGE_RATE_RATIO,
    charge_eff: float = DEFAULT_CHARGE_EFF,
    discharge_eff: float = DEFAULT_DISCHARGE_EFF,
) -> Dict[str, Any]:
    """Simulate the hourly energy balance for a wind/PV/storage system."""
    total_hours = len(load_series)
    state = {"storage_soc": storage_initial_soc_ratio * storage_capacity_mwh}

    wind_used = np.zeros(total_hours)
    pv_used = np.zeros(total_hours)
    storage_discharge = np.zeros(total_hours)
    storage_charge = np.zeros(total_hours)
    grid_purchase = np.zeros(total_hours)
    curtailment = np.zeros(total_hours)
    storage_soc = np.zeros(total_hours)
    wind_generation = np.zeros(total_hours)
    pv_generation = np.zeros(total_hours)
    wind_to_storage_input = np.zeros(total_hours)
    pv_to_storage_input = np.zeros(total_hours)

    for hour in range(total_hours):
        state = update_system(
            state=state,
            load_val=float(load_series[hour]),
            wind_pu=float(wind_pu_series[hour]),
            pv_pu=float(pv_pu_series[hour]),
            wind_capacity_mw=wind_capacity_mw,
            pv_capacity_mw=pv_capacity_mw,
            storage_capacity_mwh=storage_capacity_mwh,
            soc_min_ratio=soc_min_ratio,
            soc_max_ratio=soc_max_ratio,
            max_charge_rate_ratio=max_charge_rate_ratio,
            max_discharge_rate_ratio=max_discharge_rate_ratio,
            charge_eff=charge_eff,
            discharge_eff=discharge_eff,
        )

        wind_used[hour] = state["wind_to_load"]
        pv_used[hour] = state["pv_to_load"]
        storage_discharge[hour] = state["storage_discharging"]
        storage_charge[hour] = state["storage_charging"]
        grid_purchase[hour] = state["grid_purchase"]
        curtailment[hour] = state["curtailment"]
        storage_soc[hour] = state["storage_soc"]
        wind_generation[hour] = state["wind_generation"]
        pv_generation[hour] = state["pv_generation"]
        wind_to_storage_input[hour] = state["wind_to_storage_input"]
        pv_to_storage_input[hour] = state["pv_to_storage_input"]

    renewable_to_load = wind_used + pv_used
    renewable_generation = wind_generation + pv_generation
    renewable_to_storage_input = wind_to_storage_input + pv_to_storage_input
    renewable_consumed = renewable_to_load + renewable_to_storage_input
    total_load = float(np.sum(load_series))
    total_green_supply = float(np.sum(renewable_to_load + storage_discharge))

    return {
        "wind_generation": wind_generation,
        "pv_generation": pv_generation,
        "wind_used": wind_used,
        "pv_used": pv_used,
        "wind_to_storage_input": wind_to_storage_input,
        "pv_to_storage_input": pv_to_storage_input,
        "storage_discharge": storage_discharge,
        "storage_charge": storage_charge,
        "grid_purchase": grid_purchase,
        "curtailment": curtailment,
        "storage_soc": storage_soc,
        "load": np.array(load_series, dtype=float),
        "summary": {
            "total_wind_generation": float(np.sum(wind_generation)),
            "total_pv_generation": float(np.sum(pv_generation)),
            "total_renewable_generation": float(np.sum(renewable_generation)),
            "total_wind_consumed": float(np.sum(wind_used + wind_to_storage_input)),
            "total_pv_consumed": float(np.sum(pv_used + pv_to_storage_input)),
            "total_renewable_consumed": float(np.sum(renewable_consumed)),
            "total_storage_discharge": float(np.sum(storage_discharge)),
            "total_storage_charge": float(np.sum(storage_charge)),
            "total_grid_purchase": float(np.sum(grid_purchase)),
            "total_curtailment": float(np.sum(curtailment)),
            "total_load": total_load,
            "green_supply": total_green_supply,
        },
    }


def evaluate(
    wind_capacity_mw: float,
    pv_capacity_mw: float,
    storage_capacity_mwh: float,
    load_series: np.ndarray,
    wind_pu_series: np.ndarray,
    pv_pu_series: np.ndarray,
    soc_min_ratio: float = DEFAULT_SOC_MIN_RATIO,
    soc_max_ratio: float = DEFAULT_SOC_MAX_RATIO,
    max_charge_rate_ratio: float = DEFAULT_MAX_CHARGE_RATE_RATIO,
    max_discharge_rate_ratio: float = DEFAULT_MAX_DISCHARGE_RATE_RATIO,
    charge_eff: float = DEFAULT_CHARGE_EFF,
    discharge_eff: float = DEFAULT_DISCHARGE_EFF,
    storage_initial_soc_ratio: float = DEFAULT_STORAGE_INITIAL_SOC_RATIO,
) -> tuple[float, float, float, float, float, float]:
    """Evaluate core generation and usage metrics for a capacity plan."""
    simulation = simulate_system(
        wind_capacity_mw=wind_capacity_mw,
        pv_capacity_mw=pv_capacity_mw,
        storage_capacity_mwh=storage_capacity_mwh,
        load_series=load_series,
        wind_pu_series=wind_pu_series,
        pv_pu_series=pv_pu_series,
        storage_initial_soc_ratio=storage_initial_soc_ratio,
        soc_min_ratio=soc_min_ratio,
        soc_max_ratio=soc_max_ratio,
        max_charge_rate_ratio=max_charge_rate_ratio,
        max_discharge_rate_ratio=max_discharge_rate_ratio,
        charge_eff=charge_eff,
        discharge_eff=discharge_eff,
    )
    summary = simulation["summary"]
    return (
        summary["total_wind_generation"],
        summary["total_pv_generation"],
        summary["total_wind_consumed"],
        summary["total_pv_consumed"],
        summary["total_storage_discharge"],
        summary["total_storage_charge"],
    )


def objective(
    x: np.ndarray,
    load_series: np.ndarray,
    wind_pu_series: np.ndarray,
    pv_pu_series: np.ndarray,
) -> float:
    """Optimization objective: minimize total installed cost."""
    wind_capacity_mw, pv_capacity_mw, storage_capacity_mwh = x
    wind_cost = 3200
    pv_cost = 2500
    storage_cost = 1500

    total_cost = (
        (wind_capacity_mw * 1000.0 * wind_cost)
        + (pv_capacity_mw * 1000.0 * pv_cost)
        + (storage_capacity_mwh * 1000.0 * storage_cost)
    )

    simulation = simulate_system(
        wind_capacity_mw=wind_capacity_mw,
        pv_capacity_mw=pv_capacity_mw,
        storage_capacity_mwh=storage_capacity_mwh,
        load_series=load_series,
        wind_pu_series=wind_pu_series,
        pv_pu_series=pv_pu_series,
    )
    if simulation["summary"]["total_renewable_generation"] < 1e-6:
        return 1e12
    if min(wind_capacity_mw, pv_capacity_mw, storage_capacity_mwh) <= 0:
        return 1e12
    return float(total_cost)


def constraint_func(
    x: np.ndarray,
    load_series: np.ndarray,
    wind_pu_series: np.ndarray,
    pv_pu_series: np.ndarray,
    target_green_ratio: float,
) -> list[float]:
    """Nonlinear constraints: limit curtailment and ensure green utilization target."""
    wind_capacity_mw, pv_capacity_mw, storage_capacity_mwh = x
    simulation = simulate_system(
        wind_capacity_mw=wind_capacity_mw,
        pv_capacity_mw=pv_capacity_mw,
        storage_capacity_mwh=storage_capacity_mwh,
        load_series=load_series,
        wind_pu_series=wind_pu_series,
        pv_pu_series=pv_pu_series,
    )
    summary = simulation["summary"]
    renewable_generation = summary["total_renewable_generation"]
    total_load = summary["total_load"]

    if renewable_generation < 1e-6 or total_load < 1e-6:
        return [1.0, 1.0]

    green_supply_ratio = summary["green_supply"] / total_load
    curtailment_ratio = summary["total_curtailment"] / renewable_generation
    return [curtailment_ratio - 0.1, target_green_ratio - green_supply_ratio]


def build_balance_timeseries(
    wind_capacity_mw: float,
    pv_capacity_mw: float,
    storage_capacity_mwh: float,
    load_series: np.ndarray,
    wind_pu_series: np.ndarray,
    pv_pu_series: np.ndarray,
) -> Dict[str, np.ndarray]:
    """Build time series data for plotting the energy balance."""
    simulation = simulate_system(
        wind_capacity_mw=wind_capacity_mw,
        pv_capacity_mw=pv_capacity_mw,
        storage_capacity_mwh=storage_capacity_mwh,
        load_series=load_series,
        wind_pu_series=wind_pu_series,
        pv_pu_series=pv_pu_series,
    )
    return {
        "pv_used": simulation["pv_used"],
        "wind_used": simulation["wind_used"],
        "storage_discharge": simulation["storage_discharge"],
        "grid_purchase": simulation["grid_purchase"],
        "storage_charge": simulation["storage_charge"],
        "load": simulation["load"],
    }


def plot_weekly_balance(
    balance: Dict[str, np.ndarray],
    output_path: str | Path,
    week_start_hour: int = 0,
    title: str = "Weekly Power Balance",
) -> None:
    """Plot the weekly power balance chart."""
    hours_per_week = 24 * 7
    total_points = len(balance["load"])
    start = int(np.clip(week_start_hour, 0, max(0, total_points - 1)))
    end = min(total_points, start + hours_per_week)
    x_values = np.arange(start, end)

    pv = balance["pv_used"][start:end]
    wind = balance["wind_used"][start:end]
    discharge = balance["storage_discharge"][start:end]
    grid = balance["grid_purchase"][start:end]
    charge = balance["storage_charge"][start:end]
    load = balance["load"][start:end]

    plt.figure(figsize=(14, 6))
    plt.stackplot(
        x_values,
        pv,
        wind,
        discharge,
        grid,
        labels=["PV to Load (MW)", "Wind to Load (MW)", "Storage Discharge (MW)", "Grid Purchase (MW)"],
        colors=["#f4b400", "#5b9bd5", "#66a63a", "#e7b6b6"],
        alpha=0.95,
    )
    plt.fill_between(x_values, 0, charge, color="#98df8a", alpha=0.75, label="Storage Charge (MW)")
    plt.plot(x_values, load, color="#7b6000", linewidth=2.2, label="Load (MW)")

    tick_step = max(1, min(24, len(x_values) // 12 if len(x_values) > 0 else 1))
    ticks = x_values[::tick_step] if len(x_values) > 0 else []
    plt.xticks(ticks, [f"H{int(value)}" for value in ticks], rotation=90)
    plt.xlabel("Time")
    plt.ylabel("Power (MW)")
    plt.title(title)
    plt.legend(ncol=3, loc="upper center", frameon=False)
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=180)
    plt.close()


def run_capacity_optimization(
    data_center_load_mw: float,
    target_green_ratio: float,
    sim_hours: Optional[int] = None,
    load_coeff_series: Optional[np.ndarray] = None,
    load_series_input: Optional[np.ndarray] = None,
    wind_pu_series_input: Optional[np.ndarray] = None,
    pv_pu_series_input: Optional[np.ndarray] = None,
    load_csv_path: Optional[str | Path] = DEFAULT_LOAD_CSV_PATH,
    wind_csv_path: Optional[str | Path] = DEFAULT_WIND_CSV_PATH,
    pv_csv_path: Optional[str | Path] = DEFAULT_PV_CSV_PATH,
    bounds=((1, 500), (1, 500), (20, 500)),
    maxiter: int = 100,
    popsize: int = 15,
    seed: int = 42,
    plot_output_path: Optional[str | Path] = None,
    week_start_hour: int = 0,
    disp: bool = False,
) -> Dict[str, Any]:
    """Optimize wind/PV/storage capacities for a target green supply ratio."""
    if data_center_load_mw <= 0:
        raise ValueError("data_center_load_mw must be > 0")

    green_target = float(target_green_ratio)
    if green_target > 1:
        green_target = green_target / 100.0
    green_target = float(np.clip(green_target, 0.0, 1.0))

    candidate_series = []

    if load_series_input is not None:
        candidate_series.append(len(load_series_input))
    elif load_coeff_series is not None:
        candidate_series.append(len(load_coeff_series))
    elif load_csv_path is not None and Path(load_csv_path).exists():
        candidate_series.append(len(_read_series(load_csv_path)))

    if wind_pu_series_input is not None:
        candidate_series.append(len(wind_pu_series_input))
    elif wind_csv_path is not None:
        candidate_series.append(len(_read_series(wind_csv_path)))

    if pv_pu_series_input is not None:
        candidate_series.append(len(pv_pu_series_input))
    elif pv_csv_path is not None:
        candidate_series.append(len(_read_series(pv_csv_path)))

    resolved_sim_hours = _resolve_sim_hours(sim_hours, *candidate_series) if candidate_series else (
        sim_hours if sim_hours is not None else DEFAULT_SIM_HOURS
    )

    sys.stdout.write("[DE] Preparing load and generation series...\n")
    sys.stdout.flush()
    load_series = _resolve_load_series(
        data_center_load_mw=data_center_load_mw,
        sim_hours=resolved_sim_hours,
        load_coeff_series=load_coeff_series,
        load_series_input=load_series_input,
        load_csv_path=load_csv_path,
    )
    wind_pu_series = _resolve_generation_series(
        sim_hours=resolved_sim_hours,
        series_input=wind_pu_series_input,
        csv_path=wind_csv_path,
        series_name="Wind",
    )
    pv_pu_series = _resolve_generation_series(
        sim_hours=resolved_sim_hours,
        series_input=pv_pu_series_input,
        csv_path=pv_csv_path,
        series_name="PV",
    )

    total_load = float(np.sum(load_series))
    if total_load <= 0:
        raise ValueError("Total load is zero after preparing load profile")

    def _objective(x: np.ndarray) -> float:
        return objective(x, load_series, wind_pu_series, pv_pu_series)

    def _constraint(x: np.ndarray) -> list[float]:
        return constraint_func(x, load_series, wind_pu_series, pv_pu_series, green_target)

    sys.stdout.write("[DE] Running differential evolution optimization...\n")
    sys.stdout.flush()
    constraint = NonlinearConstraint(_constraint, -np.inf, 0)
    result = differential_evolution(
        _objective,
        bounds,
        constraints=(constraint,),
        seed=seed,
        maxiter=maxiter,
        popsize=popsize,
        disp=disp,
    )

    constraint_violation = float(getattr(result, "constr_violation", 0.0) or 0.0)
    if not result.success and constraint_violation > 1e-6:
        raise RuntimeError(f"Optimization failed: {result.message}")

    x_opt = result.x
    simulation = simulate_system(
        wind_capacity_mw=float(x_opt[0]),
        pv_capacity_mw=float(x_opt[1]),
        storage_capacity_mwh=float(x_opt[2]),
        load_series=load_series,
        wind_pu_series=wind_pu_series,
        pv_pu_series=pv_pu_series,
    )
    summary = simulation["summary"]
    green_supply_ratio = summary["green_supply"] / total_load
    curtailment_ratio = (
        summary["total_curtailment"] / summary["total_renewable_generation"]
        if summary["total_renewable_generation"] > 1e-9
        else 1.0
    )

    plot_path_str = None
    if plot_output_path is not None:
        sys.stdout.write("[DE] Rendering power balance plot...\n")
        sys.stdout.flush()
        balance = build_balance_timeseries(
            wind_capacity_mw=float(x_opt[0]),
            pv_capacity_mw=float(x_opt[1]),
            storage_capacity_mwh=float(x_opt[2]),
            load_series=load_series,
            wind_pu_series=wind_pu_series,
            pv_pu_series=pv_pu_series,
        )
        plot_weekly_balance(balance, output_path=plot_output_path, week_start_hour=week_start_hour)
        plot_path_str = str(Path(plot_output_path))
        sys.stdout.write(f"[DE] Plot saved: {plot_path_str}\n")
        sys.stdout.flush()

    return {
        "wind_capacity_mw": float(x_opt[0]),
        "pv_capacity_mw": float(x_opt[1]),
        "storage_capacity_mwh": float(x_opt[2]),
        "total_cost": float(result.fun),
        "green_supply_ratio": float(green_supply_ratio),
        "curtailment_ratio": float(curtailment_ratio),
        "target_green_ratio": green_target,
        "avg_load_mw": float(np.mean(load_series)),
        "peak_load_mw": float(np.max(load_series)),
        "grid_purchase_mwh": float(summary["total_grid_purchase"]),
        "renewable_generation_mwh": float(summary["total_renewable_generation"]),
        "renewable_consumed_mwh": float(summary["total_renewable_consumed"]),
        "storage_discharge_mwh": float(summary["total_storage_discharge"]),
        "storage_charge_mwh": float(summary["total_storage_charge"]),
        "sim_hours": int(resolved_sim_hours),
        "plot_path": plot_path_str,
    }


if __name__ == "__main__":
    output_path = OUTPUT_DIR / "de_weekly_power_balance.png"
    try:
        result = run_capacity_optimization(
            data_center_load_mw=40.0,
            target_green_ratio=0.3,
            sim_hours=DEFAULT_SIM_HOURS,
            plot_output_path=output_path,
            week_start_hour=0,
            maxiter=100,
            popsize=15,
            disp=True,
        )
        print("Optimization result:")
        print(result)
    except Exception as exc:
        print(f"Optimization demo failed: {exc}")
        print(
            "Please make sure Load.csv, Wind.csv and PV.csv are available under "
            f"{CSV_DIR} before running DE.py directly."
        )
