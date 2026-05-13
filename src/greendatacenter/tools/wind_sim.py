import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple

import pandas as pd
import requests
from geopy.geocoders import Nominatim

TOOLS_DIR = Path(__file__).resolve().parent
CSV_DIR = TOOLS_DIR / "csv"


def _build_fallback_weather_data(
    lat: float,
    start_date: str,
    end_date: str,
    timezone: str,
) -> pd.DataFrame:
    """Build a deterministic offline wind-speed profile when online weather is unavailable."""
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(hours=23)
    time_index = pd.date_range(start=start_ts, end=end_ts, freq="h", tz=timezone)

    wind_values = []
    base_speed = 5.8 + min(2.2, abs(lat - 30.0) / 25.0)
    for ts in time_index:
        day_of_year = ts.timetuple().tm_yday
        hour = ts.hour
        seasonal = 0.9 + 0.18 * math.sin((2 * math.pi * (day_of_year + 20)) / 365.0)
        diurnal = 0.85 + 0.25 * math.sin((2 * math.pi * (hour - 1)) / 24.0)
        gust = 0.35 * math.sin((2 * math.pi * (day_of_year * 24 + hour)) / 72.0)
        wind_values.append(round(max(0.5, base_speed * seasonal * diurnal + gust), 3))

    return pd.DataFrame({"wind_speed_100m": wind_values}, index=time_index)


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
        geolocator = Nominatim(user_agent="green_data_center_wind_sim")
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
        sys.stdout.write(f"[wind_sim] Geocoding failed for '{city}', using default location\n")
        sys.stdout.flush()

    # 如果所有方法都失败，返回默认位置（北京）
    return {"lat": 39.9042, "lon": 116.4074, "altitude": 50.0, "timezone": "Asia/Shanghai"}


def _resolve_time_range(
    date: Optional[str],
    mode: Literal["24h", "8760h"],
    year: Optional[int],
) -> Tuple[str, str]:
    if mode == "24h":
        selected_date = date or "2025-06-21"
        return selected_date, selected_date

    resolved_year = 2025 if year is None else year
    return f"{resolved_year}-01-01", f"{resolved_year}-12-31"


def _fetch_weather_data(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch 100m wind speed time series from Open-Meteo archive API."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "wind_speed_100m",
        "timezone": "auto",
    }
    response = requests.get(url, params=params, timeout=8)
    response.raise_for_status()
    data = response.json()

    if "hourly" not in data:
        raise ValueError("Open-Meteo response missing 'hourly' field.")
    if "time" not in data["hourly"] or "wind_speed_100m" not in data["hourly"]:
        raise ValueError("Open-Meteo response missing fields: ['time', 'wind_speed_100m']")

    weather_df = pd.DataFrame(
        {
            "time": pd.to_datetime(data["hourly"]["time"]),
            "wind_speed_100m": data["hourly"]["wind_speed_100m"],
        }
    )
    weather_df.set_index("time", inplace=True)
    return weather_df


def _load_weather_data_with_fallback(
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
    timezone: str,
) -> Tuple[pd.DataFrame, str]:
    try:
        return _fetch_weather_data(lat, lon, start_date, end_date), "open-meteo"
    except Exception as exc:
        sys.stdout.write(f"[wind_sim] Weather fetch failed, using offline fallback: {exc}\n")
        sys.stdout.flush()
        return _build_fallback_weather_data(lat, start_date, end_date, timezone), "offline-fallback"


def _wind_speed_to_coefficient(
    wind_speed_series: pd.Series,
    cut_in_ms: float,
    rated_ms: float,
    cut_out_ms: float,
) -> pd.Series:
    """Map wind speed to a simplified normalized power coefficient."""
    if rated_ms <= cut_in_ms:
        raise ValueError("rated_ms must be greater than cut_in_ms")
    if cut_out_ms <= rated_ms:
        raise ValueError("cut_out_ms must be greater than rated_ms")

    wind_speed = pd.to_numeric(wind_speed_series, errors="coerce").fillna(0.0).clip(lower=0.0)
    coefficient = pd.Series(0.0, index=wind_speed.index)

    ramp_mask = (wind_speed >= cut_in_ms) & (wind_speed < rated_ms)
    coefficient.loc[ramp_mask] = ((wind_speed.loc[ramp_mask] - cut_in_ms) / (rated_ms - cut_in_ms)) ** 3

    rated_mask = (wind_speed >= rated_ms) & (wind_speed < cut_out_ms)
    coefficient.loc[rated_mask] = 1.0

    return coefficient.clip(lower=0.0, upper=1.0)


def generate_wind_profile(
    city: str,
    date: Optional[str] = None,
    mode: Literal["24h", "8760h"] = "8760h",
    year: Optional[int] = 2025,
    cut_in_ms: float = 3.0,
    rated_ms: float = 12.0,
    cut_out_ms: float = 25.0,
    save_csv: bool = True,
    csv_output_path: Optional[os.PathLike[str] | str] = None,
) -> Dict[str, Any]:
    """Generate a wind power coefficient profile and optionally save it to CSV."""
    sys.stdout.write(f"[wind_sim] Resolving location for {city}\n")
    sys.stdout.flush()
    loc_info = _get_location_info(city)
    sim_start, sim_end = _resolve_time_range(date=date, mode=mode, year=year)
    sys.stdout.write(f"[wind_sim] Fetching weather data {sim_start} -> {sim_end}\n")
    sys.stdout.flush()

    weather_df, weather_source = _load_weather_data_with_fallback(
        loc_info["lat"],
        loc_info["lon"],
        sim_start,
        sim_end,
        loc_info["timezone"],
    )
    if weather_df.index.tz is None:
        weather_df = weather_df.tz_localize(loc_info["timezone"])
    else:
        weather_df = weather_df.tz_convert(loc_info["timezone"])

    if mode == "8760h" and len(weather_df) > 8760:
        weather_df = weather_df.iloc[:8760]
    if mode == "8760h" and len(weather_df) < 8760:
        raise ValueError(f"8760h mode requires at least 8760 points, got {len(weather_df)}")

    sys.stdout.write("[wind_sim] Computing wind power coefficients...\n")
    sys.stdout.flush()
    coefficient_series = _wind_speed_to_coefficient(
        weather_df["wind_speed_100m"],
        cut_in_ms=cut_in_ms,
        rated_ms=rated_ms,
        cut_out_ms=cut_out_ms,
    )

    result_data = []
    for index, (timestamp, coefficient) in enumerate(coefficient_series.items()):
        result_data.append(
            {
                "index": index,
                "hour": timestamp.hour,
                "timestamp": timestamp.isoformat(),
                "wind_speed_100m": round(float(weather_df.loc[timestamp, "wind_speed_100m"]), 3),
                "coefficient": round(float(coefficient), 6),
            }
        )

    csv_path = None
    if save_csv:
        if csv_output_path is None:
            CSV_DIR.mkdir(parents=True, exist_ok=True)
            csv_output_path = CSV_DIR / "Wind.csv"

        csv_path = Path(csv_output_path)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"coefficient": [row["coefficient"] for row in result_data]}).to_csv(
            csv_path,
            index=False,
            header=False,
            encoding="utf-8-sig",
        )
        sys.stdout.write(f"[wind_sim] Wind profile saved: {csv_path}\n")
        sys.stdout.flush()

    return {
        "status": "success",
        "location": f"{city} ({loc_info['lat']}, {loc_info['lon']})",
        "mode": mode,
        "csv_output_path": str(csv_path) if csv_path is not None else None,
        "time_range": {
            "start_date": sim_start,
            "end_date": sim_end,
            "points": len(result_data),
        },
        "summary": {
            "avg_coefficient": round(float(coefficient_series.mean()), 6),
            "max_coefficient": round(float(coefficient_series.max()), 6),
            "weather_source": weather_source,
        },
        "hourly_curve": result_data,
    }


if __name__ == "__main__":
    demo = generate_wind_profile(city="北京", mode="8760h", year=2025)
    print(
        "wind_sim finished:",
        {
            "location": demo["location"],
            "points": demo["time_range"]["points"],
            "avg_coefficient": demo["summary"]["avg_coefficient"],
            "csv": demo["csv_output_path"],
        },
    )
