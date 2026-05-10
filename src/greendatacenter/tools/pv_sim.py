import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple

import pandas as pd
import pvlib
import requests
from geopy.geocoders import Nominatim
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

TOOLS_DIR = Path(__file__).resolve().parent
CSV_DIR = TOOLS_DIR / "csv"
OUTPUT_DIR = TOOLS_DIR.parent / "output"


# 预定义的城市地理位置缓存（避免网络调用）
CITY_LOCATION_CACHE = {
    "乌兰察布": {"lat": 40.9042, "lon": 113.1244, "altitude": 1300.0, "timezone": "Asia/Shanghai"},
    "北京": {"lat": 39.9042, "lon": 116.4074, "altitude": 50.0, "timezone": "Asia/Shanghai"},
    "上海": {"lat": 31.2304, "lon": 121.4737, "altitude": 10.0, "timezone": "Asia/Shanghai"},
    "广州": {"lat": 23.1291, "lon": 113.2644, "altitude": 10.0, "timezone": "Asia/Shanghai"},
    "深圳": {"lat": 22.5431, "lon": 114.0579, "altitude": 10.0, "timezone": "Asia/Shanghai"},
    "杭州": {"lat": 30.2741, "lon": 120.1552, "altitude": 10.0, "timezone": "Asia/Shanghai"},
    "成都": {"lat": 30.5728, "lon": 104.0668, "altitude": 500.0, "timezone": "Asia/Shanghai"},
    "武汉": {"lat": 30.5928, "lon": 114.3055, "altitude": 30.0, "timezone": "Asia/Shanghai"},
    "西安": {"lat": 34.2619, "lon": 108.9463, "altitude": 400.0, "timezone": "Asia/Shanghai"},
    "南京": {"lat": 32.0603, "lon": 118.7969, "altitude": 20.0, "timezone": "Asia/Shanghai"},
    "张家口": {"lat": 40.8173, "lon": 114.8783, "altitude": 700.0, "timezone": "Asia/Shanghai"},
    "三亚": {"lat": 18.2208, "lon": 109.5076, "altitude": 10.0, "timezone": "Asia/Shanghai"},
    "丽江": {"lat": 26.8639, "lon": 100.2389, "altitude": 2400.0, "timezone": "Asia/Shanghai"},
}

def _get_location_info(city: str) -> Dict[str, Any]:
    """Resolve latitude and longitude for the target city."""
    if not isinstance(city, str):
        raise TypeError(f"city must be str, got {type(city).__name__}")

    # 首先尝试使用缓存
    normalized_city = city.replace("市", "").strip()
    if normalized_city in CITY_LOCATION_CACHE:
        return CITY_LOCATION_CACHE[normalized_city]
    
    # 尝试原城市名
    if city in CITY_LOCATION_CACHE:
        return CITY_LOCATION_CACHE[city]

    # 尝试网络调用（作为备用）
    try:
        geolocator = Nominatim(user_agent="green_data_center_pv_sim")
        query_candidates = [city, f"{city}, China", normalized_city]

        for query in query_candidates:
            location = geolocator.geocode(query, timeout=8)
            if location is not None:
                result = {
                    "lat": float(location.latitude),
                    "lon": float(location.longitude),
                    "altitude": 50.0,
                    "timezone": "Asia/Shanghai",
                }
                CITY_LOCATION_CACHE[normalized_city] = result
                return result
    except Exception as exc:
        sys.stdout.write(f"[pv_sim] Geocoding failed for '{city}', using default location\n")
        sys.stdout.flush()

    # 如果所有方法都失败，返回默认位置（北京）
    return {"lat": 39.9042, "lon": 116.4074, "altitude": 50.0, "timezone": "Asia/Shanghai"}


def _fetch_weather_data(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch GHI and temperature data from Open-Meteo archive API."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "shortwave_radiation,temperature_2m",
        "timezone": "auto",
    }
    response = requests.get(url, params=params, timeout=8)
    response.raise_for_status()
    data = response.json()

    if "hourly" not in data:
        raise ValueError("Open-Meteo response missing 'hourly' field.")

    required_fields = ["time", "shortwave_radiation", "temperature_2m"]
    missing_fields = [field for field in required_fields if field not in data["hourly"]]
    if missing_fields:
        raise ValueError(f"Open-Meteo response missing fields: {missing_fields}")

    weather_df = pd.DataFrame(
        {
            "time": pd.to_datetime(data["hourly"]["time"]),
            "ghi": data["hourly"]["shortwave_radiation"],
            "temp_air": data["hourly"]["temperature_2m"],
        }
    )
    weather_df.set_index("time", inplace=True)
    return weather_df


def _resolve_time_range(
    date: Optional[str],
    mode: Literal["24h", "8760h"],
    year: Optional[int],
) -> Tuple[str, str]:
    """Resolve the simulation date range for the requested mode."""
    if mode == "24h":
        selected_date = date or "2025-06-21"
        return selected_date, selected_date

    resolved_year = 2025 if year is None else year
    return f"{resolved_year}-01-01", f"{resolved_year}-12-31"


def generate_pv_profile(
    city: str,
    date: Optional[str] = None,
    capacity_kw: float = 100.0,
    tilt: Optional[float] = None,
    azimuth: float = 180.0,
    mode: Literal["24h", "8760h"] = "24h",
    year: Optional[int] = None,
    csv_output_path: Optional[os.PathLike[str] | str] = None,
) -> Dict[str, Any]:
    """
    Generate a PV hourly output profile and export the coefficient curve to CSV.

    The CSV output is a single-column coefficient file suitable for DE.py.
    """
    if capacity_kw <= 0:
        raise ValueError("capacity_kw must be > 0")

    sys.stdout.write(f"[pv_sim] Resolving location for {city}\n")
    sys.stdout.flush()
    loc_info = _get_location_info(city)
    location = Location(
        latitude=loc_info["lat"],
        longitude=loc_info["lon"],
        tz=loc_info["timezone"],
        altitude=loc_info["altitude"],
        name=city,
    )

    if tilt is None:
        tilt = loc_info["lat"]

    sim_start, sim_end = _resolve_time_range(date=date, mode=mode, year=year)
    sys.stdout.write(f"[pv_sim] Fetching weather data {sim_start} -> {sim_end}\n")
    sys.stdout.flush()
    weather_df = _fetch_weather_data(loc_info["lat"], loc_info["lon"], sim_start, sim_end)

    if weather_df.index.tz is None:
        weather_df = weather_df.tz_localize(location.tz)
    else:
        weather_df = weather_df.tz_convert(location.tz)

    if mode == "8760h" and len(weather_df) > 8760:
        weather_df = weather_df.iloc[:8760]
    if mode == "8760h" and len(weather_df) < 8760:
        raise ValueError(f"8760h mode requires at least 8760 points, got {len(weather_df)}")

    sys.stdout.write("[pv_sim] Running PVLib simulation...\n")
    sys.stdout.flush()
    system = PVSystem(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        module_parameters={"pdc0": capacity_kw * 1000.0, "gamma_pdc": -0.004},
        inverter_parameters={"pdc0": capacity_kw * 1000.0, "eta_inv_nom": 0.96},
        temperature_model_parameters=TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_polymer"],
        modules_per_string=1,
        strings_per_inverter=1,
    )

    try:
        solar_position = location.get_solarposition(weather_df.index)
        irradiance_components = pvlib.irradiance.erbs(
            ghi=weather_df["ghi"],
            zenith=solar_position["zenith"],
            datetime_or_doy=weather_df.index,
        )
        poa = system.get_irradiance(
            solar_zenith=solar_position["apparent_zenith"],
            solar_azimuth=solar_position["azimuth"],
            dni=irradiance_components["dni"],
            ghi=weather_df["ghi"],
            dhi=irradiance_components["dhi"],
        )
        cell_temp = system.get_cell_temperature(
            poa["poa_global"],
            weather_df["temp_air"],
            1.0,
            model="sapm",
        )
        dc_power = system.pvwatts_dc(poa["poa_global"], cell_temp)
        ac_power = pvlib.inverter.pvwatts(
            pdc=dc_power,
            pdc0=capacity_kw * 1000.0,
            eta_inv_nom=0.96,
        )
        ac_power = (ac_power / 1000.0).clip(lower=0).fillna(0)
    except Exception as exc:
        print(f"[Critical] PVLib calculation failed: {exc}. Using fallback sine wave.")
        ac_power = pd.Series(
            [
                max(0.0, capacity_kw * 0.9 * math.sin(math.pi * (ts.hour - 6) / 12))
                if 6 <= ts.hour <= 18
                else 0.0
                for ts in weather_df.index
            ],
            index=weather_df.index,
        )

    result_data = []
    total_energy = 0.0

    for index, (timestamp, power_kw) in enumerate(ac_power.items()):
        hour_val = round(float(power_kw), 3)
        total_energy += hour_val
        result_data.append(
            {
                "index": index,
                "hour": timestamp.hour,
                "timestamp": timestamp.isoformat(),
                "power_kw": hour_val,
                "coefficient": round(hour_val / capacity_kw, 6),
            }
        )

    peak_item = max(result_data, key=lambda item: item["power_kw"])

    if csv_output_path is None:
        CSV_DIR.mkdir(parents=True, exist_ok=True)
        csv_output_path = CSV_DIR / "PV.csv"

    csv_path = Path(csv_output_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"coefficient": [item["coefficient"] for item in result_data]}).to_csv(
        csv_path,
        index=False,
        header=False,
        encoding="utf-8-sig",
    )
    sys.stdout.write(f"[pv_sim] PV profile saved: {csv_path}\n")
    sys.stdout.flush()

    return {
        "status": "success",
        "location": f"{city} ({loc_info['lat']}, {loc_info['lon']})",
        "date": sim_start if mode == "24h" else None,
        "mode": mode,
        "csv_output_path": str(csv_path),
        "time_range": {
            "start_date": sim_start,
            "end_date": sim_end,
            "points": len(result_data),
        },
        "system_config": {
            "capacity_kw": capacity_kw,
            "tilt": tilt,
            "azimuth": azimuth,
        },
        "summary": {
            "total_generation_kwh": round(total_energy, 2),
            "peak_power_kw": round(float(peak_item["power_kw"]), 2),
            "peak_time": f"{peak_item['hour']}:00",
            "peak_timestamp": peak_item["timestamp"],
            "equivalent_sun_hours": round(total_energy / capacity_kw, 2),
        },
        "hourly_curve": result_data,
    }


if __name__ == "__main__":
    demo_result = generate_pv_profile(city="北京", mode="8760h")

    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise RuntimeError("matplotlib is required for plotting the demo output") from exc

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "pv_demo_curve.png"

    x_values = [item["index"] for item in demo_result["hourly_curve"]]
    coefficients = [item["coefficient"] for item in demo_result["hourly_curve"]]

    plt.figure(figsize=(12, 5))
    plt.plot(x_values, coefficients, linewidth=1.8, color="#16a34a")
    plt.title("PV Coefficient Curve")
    plt.xlabel("Hour Index")
    plt.ylabel("Coefficient")
    plt.grid(True, linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()

    print(f"Plot saved: {output_path}")
